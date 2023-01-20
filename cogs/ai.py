# most of these are APIs

# if you can't find a variable used in this file its probably imported from here
from config import *

# this shit is kind of dumb i wanna find a better way
global request_is_processing
request_is_processing = False

class ai(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['15', '15tts'], description="Sends AI sentences using a very real and legitimate 15.ai API.", brief="Use 15.ai to generate funny sentences")
    async def fifteen(self, ctx, *, msg):
        def check(msg):
            return msg.author == ctx.author
        global request_is_processing
        blacklist = [1, 2]
        if ctx.author.id in blacklist:
            await ctx.send("You've been blacklisted from this command")
            return
        else:
            if request_is_processing is True:
                await ctx.reply(
                    "Please allow the previous synthesis to finish.",
                    delete_after=10,
                    mention_author=True,
                )
                return
            try:
                await ctx.send('Which voice would you like? (It is case sensitive!)')
                msgfunc = await self.client.wait_for("message", check=check, timeout=30)
                requested_speaker = msgfunc.content
            except asyncio.TimeoutError:
                await ctx.send("Sorry, you didn't reply in time!")
                return
            await ctx.send("Processing... This could take a while...")
            request_is_processing = True
        FifteenAPI().save_to_file(f"{requested_speaker}", f"{msg}", f"{dannybot}\\cache\\15_output.wav")
        await ctx.reply(file=discord.File(f"{dannybot}\\cache\\15_output.wav"), mention_author=True)
        await ctx.send("This command is powered by 15.ai ^^^ https://twitter.com/fifteenai")
        request_is_processing = False
        return


    @commands.command()
    async def dalle(self, ctx, *, prompt):
        # rotty shit
        images = None
        attempt = 0
        print("-------------------------------------")
        print(f'Dalle command ran with prompt "{prompt}"')
        while not images:
            if attempt > 0:
                print(
                    f'Image generate request failed on attempt {attempt} for prompt "{prompt}"'
                )
            attempt += 1
            images = await generate_images(prompt)
            print(
                f'Successfully started image generation with prompt "{prompt}" on attempt {attempt}'
            )
            prompt_hyphenated = prompt.replace(" ", "-")
            collage = await make_collage(images, 3)
            b = collage
            collage = discord.File(
                collage, filename=f"{prompt_hyphenated}.{DALLE_FORMAT}")
            print("Sending image...")
            await ctx.reply(file=collage, mention_author=True)
            print("Caching image...")
            with open(f"{dannybot}\\cache\\dalle.png", "wb") as f:
                b.seek(0)
                f.write(b.read())
                f.close
                print("Image Cache successful")
                print("-------------------------------------")

async def setup(bot: commands.Bot):
    await bot.add_cog(ai(bot))
