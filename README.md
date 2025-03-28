# Xtract-Pirate-Bot 🏴‍☠️

A versatile Telegram bot that can download media content from various social media platforms. Supports YouTube, Instagram, Reddit, Pinterest, and Spotify. Arrr! Let's plunder some content! 🦜

## Features

- **Multi-Platform Support**
  - YouTube videos and shorts
  - Instagram posts, reels, and stories
  - Reddit posts and comments
  - Pinterest pins and boards
  - Spotify songs and playlists

- **Advanced Features**
  - Multiple quality options for video downloads
  - Batch downloads from playlists/collections
  - Progress updates during downloads
  - Download history tracking
  - Usage statistics
  - Organized folder structure
  - Automatic file cleanup

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Rahul-Sahani04/Xtract-Pirate-Bot.git
cd Xtract-Pirate-Bot
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your API credentials:
     - Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
     - Instagram credentials (optional, for private content)
     - Reddit API credentials (from [Reddit Apps](https://www.reddit.com/prefs/apps))
     - Spotify API credentials (from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard))

4. Configure download settings in `.env` (optional):
   ```bash
   # Download Settings
   MAX_DOWNLOADS=10       # Maximum items in batch/playlist
   DOWNLOAD_TIMEOUT=300   # Timeout in seconds
   CLEANUP_AFTER_SEND=true # Delete files after sending
   ```

5. Run the bot:
```bash
python bot.py
```

## Usage

1. Start the bot in Telegram: `/start`
2. Send any supported URL to download content
3. Select quality options if prompted
4. Wait for your download

### Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/stats` - Show download statistics
- `/history` - View download history
- `/settings` - Configure download preferences

## Supported URL Formats

### YouTube
- Regular videos: `https://www.youtube.com/watch?v=VIDEO_ID`
- Shorts: `https://www.youtube.com/shorts/VIDEO_ID`
- Playlists: `https://www.youtube.com/playlist?list=PLAYLIST_ID`

### Instagram
- Posts (regular): `https://www.instagram.com/p/POST_ID/`
- Pins (short URL): `https://pin.it/SHORTCODE`
- Boards: `https://www.pinterest.com/USERNAME/BOARD_NAME/`

### Reddit
- Posts: `https://www.reddit.com/r/SUBREDDIT/comments/POST_ID/`
- Subreddits: `https://www.reddit.com/r/SUBREDDIT/`

### Pinterest
- Pins (regular): `https://www.pinterest.com/pin/PIN_ID/`
- Pins (short URL): `https://pin.it/SHORTCODE`
- Boards: `https://www.pinterest.com/USERNAME/BOARD_NAME/`

### Spotify
- Tracks: `https://open.spotify.com/track/TRACK_ID`
- Playlists: `https://open.spotify.com/playlist/PLAYLIST_ID`
- Albums: `https://open.spotify.com/album/ALBUM_ID`

## API Requirements

1. **Telegram Bot API**
   - Create a bot through [@BotFather](https://t.me/BotFather)
   - Get the bot token and add it to `.env` as `BOT_TOKEN`
   - No rate limits for bot API tokens

2. **Instagram** (Optional, for private content)
   - Personal account credentials
   - Add to `.env` as `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`
   - No official API used, uses web scraping
   - Be cautious with rate limits

3. **Reddit API**
   - Create an app at [Reddit Apps](https://www.reddit.com/prefs/apps)
   - Get client ID and client secret
   - Add to `.env` as `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`
   - Rate limits: 60 requests/minute

4. **Pinterest**
   - No official API required
   - Uses web scraping
   - Be mindful of rate limits

5. **Spotify API**
   - Create an app in [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Get client ID and client secret
   - Add to `.env` as `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
   - Rate limits: Varies by endpoint

## Configuration

All configuration is managed through environment variables in the `.env` file:

```bash
# Telegram Bot Token
BOT_TOKEN=your_bot_token_here

# Instagram Credentials (Optional)
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent

# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

# Download Settings
MAX_DOWNLOADS=10
DOWNLOAD_TIMEOUT=300
CLEANUP_AFTER_SEND=true
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Author

👨‍💻 **Rahul Sahani**
- GitHub: [@Rahul-Sahani04](https://github.com/Rahul-Sahani04)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for educational purposes only. Be sure to comply with each platform's terms of service and API usage guidelines. The developers are not responsible for any misuse of this bot.