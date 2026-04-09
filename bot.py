import logging
import datetime
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from app import create_app, db
from app.models import Task, User
from config import Config

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app_flask = create_app()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != Config.TELEGRAM_ADMIN_ID:
        await update.message.reply_text("Unauthorized access.")
        return
    await update.message.reply_text("Welcome! I am your personal dashboard assistant.\nUse /tasks to see your tasks.")

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != Config.TELEGRAM_ADMIN_ID:
        await update.message.reply_text("Unauthorized access.")
        return

    # Use Flask app context to query DB
    with app_flask.app_context():
        # Assuming single user or filtering by admin ID if stored in User model
        # For simplicity, we fetch all tasks or tasks for the admin user if linked
        # Here we just fetch all tasks for demonstration or link user_id manually
        # Ideally, User model should store telegram_id, but prompt said "hardcoded or configurable" validation
        
        # We'll fetch tasks for the first user or all tasks
        pending_tasks = Task.query.filter_by(completed=False).order_by(Task.due_date).all()
        
        if not pending_tasks:
            await update.message.reply_text("You have no pending tasks.")
            return

        message = "📅 *Your Pending Tasks:*\n\n"
        for task in pending_tasks:
            message += f"• *{task.title}* - {task.due_date.strftime('%Y-%m-%d %H:%M')}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')

async def check_due_tasks(context: ContextTypes.DEFAULT_TYPE):
    with app_flask.app_context():
        now = datetime.datetime.utcnow()
        # Find tasks due in the next minute (or recently passed and not notified)
        # Detailed logic: find uncompleted tasks due <= now and maybe not notified?
        # For simplicity: find tasks due within a small window or just "due" and maybe mark as notified?
        # The prompt says: "Quando arriva la data/ora di un task: Mi manda un messaggio"
        
        # We need a way to track if notified. Adding a flag or just checking precise time window.
        # Checking precise time window in a job running every minute:
        # due_date between now-1min and now
        
        start_window = now - datetime.timedelta(minutes=1)
        tasks_due = Task.query.filter(Task.due_date <= now, Task.due_date > start_window, Task.completed == False).all()
        
        for task in tasks_due:
            # Send message
            if Config.TELEGRAM_ADMIN_ID:
                await context.bot.send_message(
                    chat_id=Config.TELEGRAM_ADMIN_ID,
                    text=f"⏰ *Remind: {task.title}*\n{task.description}",
                    parse_mode='Markdown'
                )

if __name__ == '__main__':
    if not Config.TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env")
        exit(1)

    application = ApplicationBuilder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    tasks_handler = CommandHandler('tasks', tasks)
    
    application.add_handler(start_handler)
    application.add_handler(tasks_handler)
    
    # Job Queue
    job_queue = application.job_queue
    job_queue.run_repeating(check_due_tasks, interval=60, first=10)
    
    print("Bot is running...")
    application.run_polling()
