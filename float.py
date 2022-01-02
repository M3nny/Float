import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import urllib.request
import asyncio, re, time, youtube_dl, redis

r = redis.Redis(host='<endpoint>',
                port='<port>',
                password='<password>')



client = commands.Bot(command_prefix = '%f ', intents = discord.Intents.all())
client.remove_command("help")
slash = SlashCommand(client, sync_commands=True)
TOKEN = '<token>'

connected = 0

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="%f help"))
    print('ready')

@client.group(invoke_without_command = True)
async def help(ctx):
    em = discord.Embed(title = "Help", description = "run %f help <command> for further information.", color = discord.Color.purple())
    em.add_field(name = "Music player", value = "p, leave")
    em.add_field(name = "Music controller", value = "pause, resume")
    await ctx.send(embed = em)

#####################################################################################
@slash.slash(name = "play", description="play some music")
async def play(ctx:SlashContext, *, url, timestamp = 0):
    global connected

    if not ctx.author.voice:
        await ctx.send('you are not connected to a voice channel')

    else:
        channel = ctx.author.voice.channel
    
        
        if connected == 1:
            await ctx.send("I'm already connected")
        else:

            tmp = url.replace(" ","+")
            query = urllib.request.urlopen("https://www.youtube.com/results?search_query="+tmp)
            firstVideo = re.findall(r"watch\?v=(\S{11})", query.read().decode())[0]
            url = "https://www.youtube.com/watch?v=" + firstVideo
            src = urllib.request.urlopen(url).read().decode()
            title = re.findall(""""title":{"simpleText":"(.*?)"}""", src)[0]
            
            await channel.connect()
            em = discord.Embed(title = "Now playing", description = "[**"+title+"**]"+"("+url+")", color = discord.Color.purple())
            em.set_image(url="https://img.youtube.com/vi/"+firstVideo+"/mqdefault.jpg")
            await ctx.send(embed = em)
            connected = 1

            ctx.voice_client.stop()
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': f'-vn -ss {timestamp}'}
            YDL_OPTIONS = {'format':"bestaudio"}
            vc = ctx.voice_client

            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                vc.play(source)
                ##############################
                n = int(r.get('songs_played'))
                r.set('songs_played', str(n+1))
                ##############################
                while vc.is_playing() and not vc.is_paused():
                    await asyncio.sleep(1) 
                else:
                    await asyncio.sleep(60) 
                    while vc.is_playing():
                        break
                    else:
                        await vc.disconnect()
                        connected = 0


@client.command(help = "play some music")
async def p(ctx, *, url, timestamp = 0):
    global connected

    if not ctx.author.voice:
        await ctx.send('you are not connected to a voice channel')

    else:
        channel = ctx.author.voice.channel
    
        
        if connected == 1:
            await ctx.send("I'm already connected")
        else:

            tmp = url.replace(" ","+")
            query = urllib.request.urlopen("https://www.youtube.com/results?search_query="+tmp)
            firstVideo = re.findall(r"watch\?v=(\S{11})", query.read().decode())[0]
            url = "https://www.youtube.com/watch?v=" + firstVideo
            src = urllib.request.urlopen(url).read().decode()
            title = re.findall(""""title":{"simpleText":"(.*?)"}""", src)[0]

            await channel.connect()
            em = discord.Embed(title = "Now playing", description = "[**"+title+"**]"+"("+url+")", color = discord.Color.purple())
            em.set_image(url="https://img.youtube.com/vi/"+firstVideo+"/mqdefault.jpg")
            await ctx.send(embed = em)
            connected = 1

            ctx.voice_client.stop()
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': f'-vn -ss {timestamp}'}
            YDL_OPTIONS = {'format':"bestaudio"}
            vc = ctx.voice_client

            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                vc.play(source)
                ##############################
                n = int(r.get('songs_played'))
                r.set('songs_played', str(n+1))
                ##############################
                while vc.is_playing() and not vc.is_paused():
                    await asyncio.sleep(1) 
                else:
                    await asyncio.sleep(60) 
                    while vc.is_playing():
                        break
                    else:
                        await vc.disconnect()
                        connected = 0

@help.command()
async def p(ctx):
    em = discord.Embed(title = "Play", description = "Plays an audio taken from a youtube video, using the slashed command it is possible to specify the timestamp of the video.", color = discord.Color.purple())
    em.add_field(name = "p", value = "%f p <youtube link> \ne.g. %f p https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    em.add_field(name = "p", value = "%f p <name of the video>")
    await ctx.send(embed = em)

#####################################################################################
@slash.slash(name = "pause", description="pause the audio")
async def pause(ctx:SlashContext):
    ctx.voice_client.pause()
    await ctx.send('in pause :pause_button:')

@client.command(help = "pause the audio")
async def pause(ctx):
    ctx.voice_client.pause()
    await ctx.send('in pause :pause_button:')

@help.command()
async def pause(ctx):
    em = discord.Embed(title = "Pause", description = "pause the audio.", color = discord.Color.purple())
    em.add_field(name = "pause", value = "%f pause")
    await ctx.send(embed = em)

#####################################################################################    
@slash.slash(name = "resume", description="resume the song")
async def resume(ctx:SlashContext):
    if not ctx.author.voice:
        await ctx.send('you are not connected to a voice channel')
    else:
        ctx.voice_client.resume()
        await ctx.send('resumed :arrow_forward:')

@client.command(help = "resume the audio")
async def resume(ctx):
    if not ctx.author.voice:
        await ctx.send('you are not connected to a voice channel')
    else:
        ctx.voice_client.resume()
        await ctx.send('resumed :arrow_forward:')

@help.command()
async def resume(ctx):
    em = discord.Embed(title = "Resume", description = "resume the audio.", color = discord.Color.purple())
    em.add_field(name = "resume", value = "%f resume")
    await ctx.send(embed = em)

#####################################################################################
@slash.slash(name = "leave", description="leaves the room")
async def leave(ctx:SlashContext):
    if not ctx.author.voice:
        await ctx.send('you are not connected to a voice channel')
    else:
        await ctx.voice_client.disconnect()
        await ctx.send('see ya :v:')
        global connected
        connected = 0

@client.command(help = "leaves the room")
async def leave(ctx):
    if not ctx.author.voice:
        await ctx.send('you are not connected to a voice channel')
    else:
        await ctx.voice_client.disconnect()
        await ctx.send('see ya :v:')
        global connected
        connected = 0

@help.command()
async def leave(ctx):
    em = discord.Embed(title = "Leave", description = "leaves the room.", color = discord.Color.purple())
    em.add_field(name = "leave", value = "%f leave")
    await ctx.send(embed = em)
#####################################################################################

client.run(TOKEN)

