import os
import asyncio
import aiohttp
import aiofiles
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import json
import re

class PinterestDownloader:
    def __init__(self, download_path: str = "downloads/pinterest"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def _resolve_short_url(self, url: str) -> str:
        """Resolve pin.it short URL to full Pinterest URL"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status == 200:
                        return str(response.url)
            return url
        except Exception:
            return url

    async def _parse_url(self, url: str) -> Dict:
        """Parse Pinterest URL to determine content type"""
        # Handle short URLs
        if "pin.it" in url:
            url = await self._resolve_short_url(url)
            
        if "/pin/" in url:
            return {"type": "pin", "id": url.split("/pin/")[1].split("/")[0]}
        elif "/board/" in url:
            parts = url.split("/board/")[1].split("/")
            return {"type": "board", "username": parts[0], "board_name": parts[1]}
        else:
            raise ValueError("Unsupported Pinterest URL")

    async def _download_file(self, url: str, filename: str) -> bool:
        """Download a file asynchronously"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        filepath = self.download_path / filename
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(await response.read())
                        return True
            return False
        except Exception:
            return False

    async def _get_pin_data(self, pin_id: str) -> Dict:
        """Extract pin data using Pinterest's internal API"""
        api_url = f"https://www.pinterest.com/pin/{pin_id}/"
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        raise Exception("Failed to fetch pin data")
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find the JSON data in the page
                    scripts = soup.find_all('script', type='application/json')
                    for script in scripts:
                        try:
                            data = json.loads(script.string)
                            if 'props' in data and 'initialReduxState' in data['props']:
                                pins = data['props']['initialReduxState']['pins']
                                if pin_id in pins:
                                    return pins[pin_id]
                        except json.JSONDecodeError:
                            continue
                    
                    raise Exception("Pin data not found")
        except Exception as e:
            raise Exception(f"Error fetching pin data: {str(e)}")

    async def download_pin(self, url: str) -> Dict:
        """Download a Pinterest pin"""
        try:
            parsed = await self._parse_url(url)
            if parsed["type"] != "pin":
                raise ValueError("URL must be a Pinterest pin")

            pin_data = await self._get_pin_data(parsed["id"])
            
            if not pin_data:
                raise Exception("Failed to get pin data")

            # Get the highest quality image URL
            image_url = pin_data.get('images', {}).get('orig', {}).get('url')
            if not image_url:
                raise Exception("No image URL found")

            # Download the image
            filename = f"pin_{parsed['id']}{Path(image_url).suffix}"
            success = await self._download_file(image_url, filename)

            if success:
                return {
                    'success': True,
                    'id': parsed["id"],
                    'title': pin_data.get('title', ''),
                    'description': pin_data.get('description', ''),
                    'path': str(self.download_path / filename),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("Failed to download image")

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def _get_board_pins(self, username: str, board_name: str) -> List[str]:
        """Get all pin IDs from a board"""
        board_url = f"https://www.pinterest.com/{username}/{board_name}/"
        pin_ids = []

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(board_url) as response:
                    if response.status != 200:
                        raise Exception("Failed to fetch board data")
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find pin IDs in the page
                    pins = soup.find_all('div', {'data-test-id': re.compile(r'pin.*')})
                    for pin in pins:
                        pin_id = pin.get('data-test-id', '').replace('pin', '')
                        if pin_id.isdigit():
                            pin_ids.append(pin_id)

            return pin_ids

        except Exception as e:
            raise Exception(f"Error fetching board data: {str(e)}")

    async def download_board(self, url: str, limit: int = None) -> List[Dict]:
        """Download all pins from a Pinterest board"""
        try:
            parsed = await self._parse_url(url)
            if parsed["type"] != "board":
                raise ValueError("URL must be a Pinterest board")

            # Get pin IDs from board
            pin_ids = await self._get_board_pins(
                parsed["username"], 
                parsed["board_name"]
            )

            if limit:
                pin_ids = pin_ids[:limit]

            results = []
            for pin_id in pin_ids:
                pin_url = f"https://www.pinterest.com/pin/{pin_id}/"
                result = await self.download_pin(pin_url)
                results.append(result)
                
                # Add a small delay to avoid rate limiting
                await asyncio.sleep(1)

            return results

        except Exception as e:
            return [{
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }]