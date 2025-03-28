import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

import config
from utils import URLValidator, DownloadTracker, FileManager, ProgressTracker
from downloaders import (
    YouTubeDownloader, InstagramDownloader, RedditDownloader,
    PinterestDownloader, SpotifyDownloader
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize downloaders
youtube_dl = YouTubeDownloader(download_path=config.YOUTUBE_DOWNLOAD_PATH)
instagram_dl = InstagramDownloader(download_path=config.INSTAGRAM_DOWNLOAD_PATH)
reddit_dl = RedditDownloader(
    client_id=config.REDDIT_CLIENT_ID,
    client_secret=config.REDDIT_CLIENT_SECRET,
    user_agent=config.REDDIT_USER_AGENT,
    download_path=config.REDDIT_DOWNLOAD_PATH
)
pinterest_dl = PinterestDownloader(download_path=config.PINTEREST_DOWNLOAD_PATH)
spotify_dl = SpotifyDownloader(
    client_id=config.SPOTIFY_CLIENT_ID,
    client_secret=config.SPOTIFY_CLIENT_SECRET,
    download_path=config.SPOTIFY_DOWNLOAD_PATH
)

# Initialize download tracker
download_tracker = DownloadTracker(config.HISTORY_FILE)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text(
        "Hello! I'm a media downloader bot. I can help you download content from various platforms.\n\n"
        "Supported platforms:\n"
        "- YouTube (videos & shorts)\n"
        "- Instagram (posts, reels, stories)\n"
        "- Reddit (posts & comments)\n"
        "- Pinterest (pins & boards)\n"
        "- Spotify (songs & playlists)\n\n"
        "Just send me a link to get started!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when the command /help is issued."""
    await update.message.reply_text(
        "How to use this bot:\n\n"
        "1. Send any supported URL\n"
        "2. Select quality options if available\n"
        "3. Wait for your download\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/stats - Show your download statistics\n"
        "/history - View download history\n"
        "/settings - Configure download preferences"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show download statistics when the command /stats is issued."""
    stats = await download_tracker.get_stats()
    
    message = (
        "📊 Download Statistics\n\n"
        f"Total Downloads: {stats['total_downloads']}\n"
        f"Successful: {stats['successful_downloads']}\n"
        f"Failed: {stats['failed_downloads']}\n"
        f"Success Rate: {stats['success_rate']:.1f}%\n\n"
        "Downloads by Platform:\n"
    )
    
    for platform, count in stats['downloads_by_platform'].items():
        message += f"- {platform.title()}: {count}\n"
    
    message += f"\nTotal Data Downloaded: {FileManager.format_size(stats['total_size_bytes'])}"
    
    await update.message.reply_text(message)

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show download history when the command /history is issued."""
    history = await download_tracker.get_history(limit=10)
    
    if not history:
        await update.message.reply_text("No download history available.")
        return

    message = "📥 Recent Downloads:\n\n"
    for item in reversed(history):
        status = "✅" if item.get('success') else "❌"
        message += (
            f"{status} {item.get('title', 'Unknown')}\n"
            f"Platform: {item.get('platform', 'Unknown')}\n"
            f"Date: {datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M')}\n\n"
        )
    
    await update.message.reply_text(message)

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings options when the command /settings is issued."""
    keyboard = [
        [
            InlineKeyboardButton("Video Quality", callback_data="settings_video_quality"),
            InlineKeyboardButton("Audio Quality", callback_data="settings_audio_quality")
        ],
        [
            InlineKeyboardButton("Download Path", callback_data="settings_download_path"),
            InlineKeyboardButton("Auto-Delete", callback_data="settings_auto_delete")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚙️ Settings:", reply_markup=reply_markup)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URLs sent to the bot."""
    url = update.message.text
    status_message = await update.message.reply_text("🔄 Processing your request...")
    
    try:
        # Validate URL
        if not URLValidator.is_valid_url(url):
            await status_message.edit_text("❌ Invalid URL. Please send a valid URL.")
            return

        # Determine platform
        platform = URLValidator.get_platform(url)
        if not platform:
            await status_message.edit_text(
                "❌ Unsupported platform. Please send a URL from a supported platform."
            )
            return

        # Update status
        await status_message.edit_text("⏳ Starting download...")

        # Handle download based on platform
        result = None
        if platform == 'youtube':
            result = await youtube_dl.download(url)
        elif platform == 'instagram':
            result = await instagram_dl.download_post(url)
        elif platform == 'reddit':
            result = await reddit_dl.download_post(url)
        elif platform == 'pinterest':
            result = await pinterest_dl.download_pin(url)
        elif platform == 'spotify':
            result = await spotify_dl.download_track(url)

        if not result or not result.get('success'):
            error_msg = result.get('error', 'Unknown error') if result else 'Download failed'
            await status_message.edit_text(f"❌ {error_msg}")
            return

        # Track download
        await download_tracker.add_download({
            'url': url,
            'platform': platform,
            'success': True,
            'title': result.get('title', 'Unknown'),
            'file_size': FileManager.get_file_size(Path(result['path']))
        })

        # Send file
        file_path = Path(result['path'])
        try:
            await status_message.edit_text("📤 Sending file...")
            
            # Ensure filename has consistent format
            title = FileManager.sanitize_filename(result.get('title', 'Unknown'))
            original_path = file_path
            file_path = original_path.parent / f"{title}{original_path.suffix}"
            
            # Rename if necessary
            if original_path != file_path and original_path.exists():
                original_path.rename(file_path)
            
            # Open file in binary mode for sending
            with open(file_path, 'rb') as file:
                # Send file based on type
                if file_path.suffix.lower() in ['.mp4', '.webm']:
                    await update.message.reply_video(
                        video=file,
                        caption=f"📹 {result.get('title', 'Video')}"
                    )
                elif file_path.suffix.lower() in ['.mp3', '.m4a', '.wav']:
                    await update.message.reply_audio(
                        audio=file,
                        caption=f"🎵 {result.get('title', 'Audio')}"
                    )
                else:
                    await update.message.reply_document(
                        document=file,
                        caption=f"📄 {result.get('title', 'File')}"
                    )

            # Cleanup if enabled
            if config.CLEANUP_AFTER_SEND:
                file_path.unlink()

            await status_message.delete()

        except FileNotFoundError:
            await status_message.edit_text("❌ File not found after download")
            logger.error(f"File not found: {file_path}")
        except Exception as e:
            await status_message.edit_text(f"❌ Error sending file: {str(e)}")
            logger.error(f"Error sending file: {str(e)}", exc_info=True)

    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}", exc_info=True)
        await status_message.edit_text(f"❌ Error: {str(e)}")
        
        # Track failed download
        await download_tracker.add_download({
            'url': url,
            'platform': platform if platform else 'unknown',
            'success': False,
            'error': str(e)
        })

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('settings_'):
        setting = query.data.replace('settings_', '')
        # Implement settings logic here
        await query.message.edit_text(f"Setting '{setting}' will be implemented soon!")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()