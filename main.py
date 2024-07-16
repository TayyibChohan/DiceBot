from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Embed
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

PRIVATE_MESSAGE_PREFIX: Final[str] = "p"
MESSAGE_PREFIX: Final[str] = os.getenv("MESSAGE_PREFIX")


intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)


async def send_message(message: Message, user_message: str) -> None:
    if is_private := user_message.startswith(PRIVATE_MESSAGE_PREFIX):
        user_message = user_message[len(PRIVATE_MESSAGE_PREFIX):]
    try:
        response = get_response(user_message)
        if len(response) == 1:
            if is_private:
                await message.author.send(response[0]) 
            else:
                await message.channel.send(response[0])
        else:
            type = response[0]
            if type == "EmbedAndFile":
                embed: Embed = response[1]
                file = response[2]
                if is_private:
                    await message.author.send(embed=embed, file=file)
                    #delete the file after sending it
                    os.remove(file.fp.name)
                else:
                    await message.channel.send(embed=embed, file=file)
                    #delete the file after sending it
                    os.remove(file.fp.name)
            elif type == "Embed":
                embed: Embed = response[1]
                if is_private:
                    await message.author.send(embed=embed)
                else:
                    await message.channel.send(embed=embed)
            else:
                raise Exception(f"Unknown response type: {type}")   
               
    except Exception as e:
        print(f"Error handling response: {e}")

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message: Message):
    # Ignore messages from the bot itself and messages that don't start with the message prefix or mention the bot
    if message.author == client.user or not (message.content.startswith(MESSAGE_PREFIX) or message.content.startswith(client.user.mention)):
        return
    
    if message.content.startswith(client.user.mention):
        message.content = message.content.replace(client.user.mention, MESSAGE_PREFIX, 1)
    
    if message.content.startswith(MESSAGE_PREFIX):
        message.content = message.content[len(MESSAGE_PREFIX):]
    
    username: str = str(message.author)
    user_message: str = str(message.content)
    channel: str = str(message.channel)
    print(f'[{channel}], {username}: ": "{user_message}"') # Log the message to the console
    
    await send_message(message, user_message)

def main() -> None:
    client.run(TOKEN)

if __name__ == "__main__":
    main()