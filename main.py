import discord
import config
import aiohttp
import asyncio
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands

class ChannelCopier(discord.Client):
    async def on_connect(self):
        copy = self.get_channel(config.channel)
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(config.webhook, adapter=AsyncWebhookAdapter(session))
            print(f'Logged in {self.user}, copying channel {copy.name} with webhook {config.webhook}.')
            messages = await copy.history(limit = 10000).flatten()
            delay = 0.6
            for message in messages[::-1]:
                try:
                    if message.content == None:
                        continue

                    reply =  message.reference
                    if reply is not None:
                        reply = await message.channel.fetch_message(message.reference.message_id)
                        author = message.author
                        timestamp = message.created_at
                        avatar_url = author.avatar_url
                        await webhook.send(content = f"""
{message.content}

Replying to `{reply.author}`:
- **{reply.content}**
                        """, username = f'{author} | {timestamp}', avatar_url = avatar_url)
                        await asyncio.sleep(delay)
                    
                    else:
                        author = message.author
                        timestamp = message.created_at
                        avatar_url = author.avatar_url
                        await webhook.send(content = message.content, username = f'{author} | {timestamp}', avatar_url = avatar_url)
                        await asyncio.sleep(delay)

                except discord.errors.HTTPException:
                    await asyncio.sleep(delay)

                except Exception as e:
                    print(e)
                    await asyncio.sleep(delay)


client = ChannelCopier()
client.run(config.token)