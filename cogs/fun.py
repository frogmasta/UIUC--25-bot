import random

from discord.ext import commands

from src.help_descriptions import _8ball_help


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['8ball'], **_8ball_help)
    async def _8ball(self, ctx, *, question):
        responses = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes – definitely', 'You may rely on it',
                     'As I see it, yes', 'Most likely', 'Outlook good', 'Signs point to yes', 'Reply hazy',
                     'Try again',
                     'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                     'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                     'Very doubtful']
        await ctx.send(f'Question: {question} \nAnswer: {random.choice(responses)}')

    @_8ball.error
    async def _8ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a question for me to answer!')
    
    @commands.command()
    async def roast(ctx,name):
        roasts =["You must be the arithmetic man; you add trouble, subtract pleasure, divide attention, and multiply ignorance.",
            "You're so fat you need cheat codes to play Wii Fit.",
            "If you were twice as smart, you'd still be stupid.",
            "You're so ugly Hello Kitty said goodbye to you.",
            "Here's 20 cents, call all your friends and give me back the change.",
            "IF SHIT LOOKED AT YOU, IT WOULD CALL YOU DADDY.",
            "YO MAMA'S BREATH IS SO STANKY, SHE EATS ODOUR EATERS.",
            "I hear when you were a child your mother wanted to hire somebody to take care of you, but the mafia wanted too much.",
            "I could eat a bowl of alphabet soup and crap out a smarter comeback than what you just said.",
            "You're as ugly as a salad!",
            "You're a failed abortion whose birth certificate is an apology from the condom factory.",
            "Your so ugly when you popped out the doctor said aww what a treasure and your mom said yeah lets bury it",
            "Some cause happiness wherever they go; others, whenever they go.",
            "You must have been born on a highway, because that's where most accidents happen.",
            "Your momma is so ugly... she gotta be your momma.",
            "You are so ugly that when your mom dropped you off at school,she got a ticket for littering.",
            "You're so fat Thanos had to snap twice"]

        selectedRoast = roasts[random.randint(0,(len(roasts)-1))]
        await ctx.send("Hey " + name + ": " + selectedRoast)



def setup(bot):
    bot.add_cog(Fun(bot))
