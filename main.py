import discord
from discord.ext import commands
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from datetime import datetime as dt
from datetime import timedelta, timezone 
import pytz
from typing import Union
import math
import io 


intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("-"),intents=intents)

class ProcessingDiscord:
    def __init__(self) -> None:
        pass

    def analize_arg(self,ctx,*args: tuple):
        self.usr = set()
        self.ch = set()
        self.days = 7
        
        if args:
            for arg in args:
                if arg is discord.Member:
                    self.usr.add(arg)
                elif arg is discord.TextChannel:
                    self.ch.add(arg)
                elif arg is int:
                    arg = math.floor(arg)
                    if 0 < arg < 8:
                        self.days = arg 
                else:           
                    pass

        # self.days をdatetime オブジェクトに変換
        self.now = dt.now(timezone.utc)
        print(self.now)
        self.date = self.now - timedelta(days=self.days)
        print(self.date.tzinfo,self.date)
        
        if not self.usr:
            self.usr.add(ctx.author)
        
        if not self.ch:
            for ch in ctx.guild.text_channels:
                self.ch.add(ch)

# コマンドをもとに必要情報の入手　(メッセージ取得、ギルドメンバー取得)
class GetMsg:
    def __init__(self,ch_history_ls ,usr):
        # メッセージのリスト
        self.ls = []
        # 全メッセージ数
        self.allmsg_count = 0
        #　抽出するメッセージ数
        self.count = 0
        for each_history in ch_history_ls:
            #ctxから各投稿のメッセージ本文のみ抽出しリスト化
            for msg_info in each_history:
                edited_dt = msg_info.created_at
                msg_author = msg_info.author
                self.allmsg_count += 1
                # メッセージが空文の場合抽出しない(エラー防止)
                if msg_author.bot:
                    continue
                elif usr:
                    if msg_author in usr:
                        self.ls.append(edited_dt)
                        self.count += 1
        print(f'🔻リストアップしたメッセージ:\n {self.ls}')
        print(f'🔻リストアップしたメッセージ数:\n {self.count}')


class BasicCommand(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
            
    @commands.command()
    async def t(self,ctx, *args: Union[discord.TextChannel, discord.Member,int,str]):
        print(args)
        # 入力された引数の分析をし、取得するchannel,member,日数を確定する。
        cmd = ProcessingDiscord()
        cmd.analize_arg(ctx,args)

        # 取得したチャンネルそれぞれについて書き込みオブジェクトを取得する
        ch_history_ls = list()
        for ch in cmd.ch:
            ch_history_ls.append(await ch.history(after =cmd.date).flatten())
        # 取得した書き込みオブジェクトから指定のチャンネル、ユーザーの物のみを抜粋
        edited_dt_ls = GetMsg(ch_history_ls,cmd.usr)
        await ctx.send(f'{cmd.days}間であなたは{len(edited_dt_ls.ls)}回書き込みました。')


bot.add_cog(BasicCommand(bot=bot))
@bot.event
async def on_ready():
    print(f'🟠ログインしました🟠')

bot.run( 'TOKEN')




'''
xlist=['2018-08-24', '2018-08-24', '2018-08-25', '2018-08-25', '2018-08-25', '2018-08-23', '2018-08-23', '2018-08-21', '2018-08-21', '2018-08-19', '2018-08-17', '2018-08-05', '2018-07-28', '2018-07-18', '2018-07-18', '2018-07-17', '2018-07-15', '2018-07-11', '2018-07-10', '2018-07-09']

ylist=['19:46:00', '3:30:00', '3:29:00', '3:26:00', '2:52:00', '14:36:00', '2:45:00', '23:27:00', '3:56:00', '4:20:00', '2:49:00', '22:47:00', '22:22:00', '13:52:00', '1:49:00', '17:48:00', '15:22:00', '2:12:00', '18:27:00', '21:15:00']


# xlist,ylistを datetime型に変換
xlist = [dt.strptime(d, '%Y-%m-%d') for d in xlist]
ylist = [dt.strptime(d, '%H:%M:%S') for d in ylist]
# データをプロット
ax = plt.subplot()
ax.scatter(xlist,ylist)
# X軸の設定 (目盛りを１日毎,範囲は 7/9～8/24とする)
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
ax.set_xlim([dt.strptime('2018-7-9','%Y-%m-%d'), dt.strptime('2018-8-24', '%Y-%m-%d')])
# Y軸の設定 (目盛りを１時間毎,範囲は 0:00～23:59とする)
ax.yaxis.set_major_locator(mdates.HourLocator())
ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax.set_ylim([dt.strptime('00:00','%H:%M'), dt.strptime('23:59','%H:%M')])
plt.xticks(rotation=90)
plt.show()
'''