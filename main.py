import discord
from discord.ext import commands
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from datetime import datetime as dt
from datetime import timedelta
from typing import Union
import math
import io 
import time 
import collections

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("-"),intents=intents)

class ProcessingDiscord:
    def __init__(self) -> None:
        pass

    def analize_arg(self,ctx,args: tuple):
        self.usr = set()
        self.ch = set()
        self.days = 7
        
        print(args)
        if args:
            for arg in args:
                print(arg,type(arg))
                if isinstance(arg,discord.Member):
                    self.usr.add(arg)
                elif isinstance(arg,discord.TextChannel):
                    self.ch.add(arg)
                elif isinstance(arg,int):
                    arg = math.floor(arg)
                    if 0 < arg < 100:
                        self.days = arg 
                else:           
                    pass

        # self.days をdatetime オブジェクトに変換
        self.now = dt.now()
        print(self.now)
        self.date = self.now - timedelta(days=self.days)
        print(self.date.tzinfo,self.date)
        # discordの仕様で必ずtimezoneは指定してはいけない。

        
        if not self.usr:
            self.usr.add(ctx.author)
        
        if not self.ch:
            for ch in ctx.guild.text_channels:
                self.ch.add(ch)
                time.sleep(0.1)
        print(self.ch,self.usr)

# コマンドをもとに必要情報の入手　(edited_time)
class GetMsg:
    def __init__(self,ch_history_ls ,usr):
        # 各メッセージの最終編集時間のリスト
        self.dtls = []
        self.chls = set()
        # 全メッセージ数
        self.allmsg_count = 0
        #　抽出するメッセージ数
        self.count = 0
        for each_history in ch_history_ls:
            #ctxから各投稿のメッセージの最終編集時間のみ抽出しリスト化
            for msg in each_history:
                edited_dt = msg.created_at
                msg_author = msg.author
                msg_channel = msg.channel
                self.allmsg_count += 1
                if msg_author.bot:
                    continue
                elif usr:
                    if msg_author in usr:
                        self.dtls.append(edited_dt)
                        self.chls.add(msg.channel)
                        self.count += 1
        print(f'🔻リストアップしたメッセージ:\n {self.dtls}')
        print(f'🔻リストアップしたメッセージ数:\n {self.count}')


class BasicCommand(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
            
    @commands.command()
    async def t(self,ctx, *args: Union[discord.TextChannel, discord.Member,int,str]):
        # 入力された引数の分析をし、取得するchannel,member,日数を確定する。
        cmd = ProcessingDiscord()
        cmd.analize_arg(ctx,args)

        # 取得したチャンネルそれぞれについて書き込みオブジェクトを取得する
        ch_history_ls = list()
        for ch in cmd.ch:
            ch_history_ls.append(await ch.history(after =cmd.date,before= cmd.now).flatten())
        # 取得した書き込みオブジェクトから指定のチャンネル、ユーザーの物のみを抜粋
        res = GetMsg(ch_history_ls,cmd.usr)
        chls = []
        for ch in res.chls:
            chls.append(ch.name)
        await ctx.send(f'```{cmd.days}日間であなたは{len(res.dtls)}回書き込みました。\n書き込んだチャンネル: \n{",".join(chls)}```')

        print(collections.Counter(res.dtls))

        """
        datals =[]
        for dt in res.dtls:
            datals.append(str(dt))
        data = ",1\n".join(datals)
        print(data)
        df = pd.read_csv(io.StringIO(data), header=None, index_col=[0])
        df['count'] = 1
        print(df.head())
        """

bot.add_cog(BasicCommand(bot=bot))
@bot.event
async def on_ready():
    print(f'🟠ログインしました🟠')

bot.run( 'TOKEN')