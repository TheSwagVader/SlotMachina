import logging
from logging import info
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='dev.log')
from telegram import Update, Bot, Message, Dice
from telegram.ext import Updater, Defaults, CallbackContext, CommandHandler, MessageHandler, Filters

class SlotMachina:
    def __init__(self):
        self.bot = Updater('1615589503:AAGprrkyGisgdjR7yy_k4fVff0Zu1LXISQM')
        self.dispatcher = self.bot.dispatcher

        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('newgame', self.newGame))
        self.dispatcher.add_handler(CommandHandler('reset', self.reset))

        self.dispatcher.add_handler(MessageHandler(Filters.dice.slot_machine, self.process))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.filter))
        
        #trash sector
        self.dispatcher.add_handler(MessageHandler(Filters.dice.dice, self.filter))
        self.dispatcher.add_handler(MessageHandler(Filters.dice.darts, self.filter))
        self.dispatcher.add_handler(MessageHandler(Filters.dice.football, self.filter))
        self.dispatcher.add_handler(MessageHandler(Filters.dice.basketball, self.filter))

        self.playerBalance = 0
        self.currentBet = 0
        self.isGameNow = False
        self.isBetGet = False

        self.winTable = {
            1: 1,
            22: 3,
            43: 10,  
            64: 50,
        }

    def start(self, update:Update, context:CallbackContext):
        info(f'Got /start from { update.message.from_user.first_name } { update.message.from_user.last_name } ({ update.message.from_user.id })')
        update.message.reply_text(
            'Приветствую. Я - SlotMachina. Бот для тех, кто хочет сорвать бабла. Вы можете начать игру(newgame)'
        )

    def newGame(self, update:Update, context:CallbackContext):
        info(f'Got /newgame from  {update.message.from_user.id}')
        self.isGameNow = True
        self.playerBalance = 100
        update.message.reply_text(f'Отлично! Давайте начнём. Ваш баланс: {self.playerBalance}$. Введите ставку:')

    def getBet(self, update:Update, context:CallbackContext):
        info(f'Got bet from  {update.message.from_user.id}')
        try:
            self.currentBet = int(update.message.text)
            self.playerBalance -= self.currentBet
            self.isBetGet = True
            update.message.reply_text(f'Вы поставили {self.currentBet}$. Теперь отправьте слот-машину.')
        except ValueError:
            update.message.reply_text('Вы ввели неправильную ставку')

    def filter(self, update:Update, context:CallbackContext):
        info(f'Got slot machine from  {update.message.from_user.id}')
        if self.isGameNow and not self.isBetGet:
            self.getBet(update, context)
        elif self.isGameNow and self.isBetGet:
            update.message.reply_text('Вы не отправили слот-машину')

    def process(self, update:Update, context:CallbackContext):
        info(f'Got slot machine from  {update.message.from_user.id}')
        if self.isGameNow and self.isBetGet:
            self.isBetGet = False
            incomingValue = update.message.dice.value
            if incomingValue not in self.winTable:
                update.message.reply_text('Вы проиграли')

            else:
                winValue = self.currentBet * self.winTable[incomingValue]
                self.playerBalance += winValue
                update.message.reply_text(f'Вы выйграли {winTable}$')
            if self.playerBalance > 0:
                update.message.reply_text(f'Ваш баланс {self.playerBalance}$. Хотите сыграть ещё? Тогда вводите ставку. Иначе - reset.')
            else:
                self.reset(update, context)
                update.message.reply_text('Похоже, у вас нет больше денег. Игра сброшена, но вы всегда можете начать новую, введя команду newgame')
        elif not self.isGameNow:
            update.message.reply_text('Вы не играете в данный момент')
        else:
            update.message.reply_text('Вы не поставили')
    
    def reset(self, update:Update, context:CallbackContext):
        info(f'Got /reset from  {update.message.from_user.id}')
        if not self.isGameNow:
            update.message.reply_text('Вы не играете в данный момент')
        else:
            self.isGameNow, self.isBetGet = False, False
            self.playerBalance, self.currentBet = 0, 0
            update.message.reply_text('Игра сброшена. Вы всегда можете начать новую, введя команду newgame')

    def run(self):
        info('Booting up bot...')
        self.bot.start_polling()
        self.bot.idle()

if __name__ == "__main__":
    bot = SlotMachina()
    bot.run()