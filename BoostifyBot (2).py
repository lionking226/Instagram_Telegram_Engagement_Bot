from http.client import FORBIDDEN
from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, ConversationHandler

import time
import asyncio
import instaloader


L = instaloader.Instaloader()
#L.login("mega__mr", "Mega_mind_7$")

L.context.max_query_frequency = 5

usernames = []
initial_likes_count = 0  # Initialize variable to store the initial number of likes

new_likes_count = 0  # Initialize variable to store the new number of likes


user_posts={}

time.sleep(5)

post_urls = ["https://www.instagram.com/p/CzKGWMePjVv/?utm_source=ig_web_copy_link",
             " https://www.instagram.com/p/BuPAR9DHw_P/?utm_source=ig_web_copy_link&igshid=N2ViNmM2MDRjNw==",
             " https://www.instagram.com/p/BxNVsU-n1HS/?utm_source=ig_web_copy_link&igshid=N2ViNmM2MDRjNw==",
             " https://www.instagram.com/p/CHGUeH-j0bI/?utm_source=ig_web_copy_link&igshid=N2ViNmM2MDRjNw==",
             " https://www.instagram.com/p/CHA0ZZcDhBs/?utm_source=ig_web_copy_link&igshid=N2ViNmM2MDRjNw==",
             " https://www.instagram.com/p/CG_cZxcDKEQ/?utm_source=ig_web_copy_link&igshid=N2ViNmM2MDRjNw==",
             " https://www.instagram.com/p/CG_J7cmjhW3/?utm_source=ig_web_copy_link&igshid=N2ViNmM2MDRjNw==",
             " https://www.instagram.com/p/CG--035jjiG/?utm_source=ig_web_copy_link&igshid=N2ViNmM2MDRjNw==",
             " https://www.instagram.com/p/CESuSMRDkQZ/?utm_source=ig_web_copy_link"
             ]


#print(post_urls)
posts_liked = []
# Your existing code...
user_initial_likes = {}
user_final_likes = {}

async def scrape_instagram_data(first_time=True):
    global usernames, initial_likes_count, new_likes_count, post_url, posts_liked, working_list
    
    
    if len(post_urls)>=10:
        recent_links = post_urls[-9:][::1]
        working_list = ["https://www.instagram.com/p/CzKGWMePjVv/?utm_source=ig_web_copy_link"] + (recent_links)
        print(working_list)
    else:
        working_list = post_urls[::1]
        print(working_list)

    new_likes_count = 0

    for post_url in working_list:
        
        if post_url in posts_liked:
            continue
        else:
            print(f"Processing Post: {post_url}")
            try:
                post = instaloader.Post.from_shortcode(L.context, post_url.split('/')[-2])
                #profile = post.owner_profile
                #followers = profile.followers
            except instaloader.exceptions.InstaloaderException as e:
                if "400 Bad Request" in str(e):
                    print("Invalid Instagram post URL or post not found.")
                else:
                    print(f"Error processing post: {e}")
                return None



            # If it's the first post, store the initial likes count
            if first_time:
                initial_likes_count = post.likes
                #initial_followers = followers
                #print(f"Followers: {initial_followers}")
                print(f"Initial Likes Count: {initial_likes_count}")
            else:
                # Store the new likes count
                new_likes_count = post.likes
                #final_followers = followers
                #print(f"Final followers: {final_followers}")
                print(f"New count: {new_likes_count}")

        await asyncio.sleep(5)

    return initial_likes_count if first_time else new_likes_count

BOT_TOKEN: Final = "6848807139:AAE9UGtmSmut0JjzBnZ8tLgDFzJ-U5SSI-E"
BOT_USERNAME: Final = "@boostifygrowthbot"

users_username = {}

RECEIVE_USERNAME, CHECK_LIKE, OTHER_TEXT = range(3)

async def start(update: Update, context: CallbackContext) -> None:

    chat_id = update.message.chat.id

    try:
        if update.message.chat.type == 'private':
            # Handle /start in private chat
            message_text = "Welcome! This is your private chat. Type /start to begin."
            await context.bot.send_message(chat_id=chat_id, text=message_text)
        else:
            # Send the list button in a group
            message_text = "Click the list button below to get the post links:"
            keyboard = [[InlineKeyboardButton("LIST 🗒", url=f"https://t.me/boost_upbot?start=start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup)
    except FORBIDDEN as e:
        print(f"User blocked the bot. Error: {e}")
    await update.message.reply_text("Hello there! Welcome to Boostify bot.  I will boost your social media post.\n"
                                    "\n"
                                    "First, please enter your Instagram username (eg; @monica) to get started.")     
    
    return RECEIVE_USERNAME
    
async def receive_instagram_username(update: Update, context: CallbackContext) -> None:
    global users_username
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    
    context.user_data['expected_username'] = True
    
    # Check if the bot is expecting a username from the user
    if 'expected_username' in context.user_data and context.user_data['expected_username']==True:
        
        instagram_username = update.message.text
        
        if not instagram_username.startswith("@"):
            await update.message.reply_text("Please provide a valid username. Make sure it starts with '@'.\n Choose /start.")
            return ConversationHandler.END
        else:
            await update.message.reply_text("Please wait for a few seconds while I pull some data and save your username...\n\nSaving username...")
            users_username[int(user_id)] = str(instagram_username)
            context.user_data['expected_username'] = False  # Reset the flag
        
            await asyncio.create_task(scrape_instagram_data(first_time=True))

            await update.message.reply_text(f"Thanks, {users_username.get(user_id)}! Your Instagram username has been saved.\nChoose (/posts_list) from the menu to get a list of posts you must like.")
            return ConversationHandler.END    
    else:
        await update.message.reply_text("I'm not expecting an Instagram username right now.\nChoose Start from the menu to get started.")
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    
        return ConversationHandler.END


async def post_list(update: Update, context: CallbackContext) -> None:
    global post_urls, working_list
    if len(post_urls)>=10:
        recent_links = post_urls[-9:][::1]
        working_list = ["https://www.instagram.com/p/CzKGWMePjVv/?utm_source=ig_web_copy_link"] + (recent_links)
        print(working_list)
    else:
        working_list = post_urls[::1]
        print(working_list)
        
    post_urls_message = "\n".join([f"{i + 1}.)  {url}" for i, url in enumerate(working_list)])
    x = "Like ALL the following posts.\n'ONCE YOU'RE DONE':\nPlease, use (/send_mylink) to post your link."
    b = '\n\n\n'
    await update.message.reply_text(f"{x}\n\n  {post_urls_message}{b}")


async def receive_instagram_post(update: Update, context: CallbackContext) -> None:
    global post_urls, user_id, chat_id, initial_likes_count, new_likes_count
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id


    # Run the scraping process again for every post
    await update.message.reply_text("Processing some data, please wait.")
    await asyncio.create_task(scrape_instagram_data(first_time=False))
    await update.message.reply_text("Please provide a link to your Instagram Post.\nPlease make sure it is sent in the following format: https://www.instagram.com/p/xxx.")
    
    return CHECK_LIKE
    
user_warnings = {}

async def Check_like(update: Update, context: CallbackContext) -> None:
    global user_id, chat_id, usernames, user_post_url, post_url, posts_liked, new_likes_count, initial_likes_count
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    group_ids= ['-1002054443776', '-1002088440346', '-1002009202976', '-1002125439245', '-1002140062322', '-1002050602690', '-1002115789119', '-1001997672377']
    
    
    user_warnings[user_id] = user_warnings.get(user_id, 0) + 1

    context.user_data["expected_post_url"] = True
    user_initial_likes[user_id] = initial_likes_count
    user_final_likes[user_id] = new_likes_count
    # Check if the bot is expecting a post URL from the user
    if 'expected_post_url' in context.user_data and context.user_data['expected_post_url'] == True:
        user_post_url = update.message.text

        # Check if the user liked all the posts
        if not int(user_final_likes.get(user_id)) >= int((user_initial_likes.get(user_id) + 1)):
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            await update.message.reply_text(f"To participate, please like ALL the Instagram posts and Follow accounts first.\n Choose start.")
            keyboard = [[InlineKeyboardButton("LIST 🗒", url=f"https://t.me/boost_upbot?start=start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            for group_id in group_ids:
                print(group_id)
                await context.bot.send_message(chat_id=int(group_id), text=f'❌ {update.message.from_user.name} you missed one or a few posts!\n Make sure to like the posts to continue.\n⚠️ Warnings: {user_warnings[user_id]}.',reply_markup=reply_markup)
            return ConversationHandler.END
            
            # End the conversation if the user didn't like all the posts
            return ConversationHandler.END
        
        # Check if the provided URL is valid
        if user_post_url.startswith("https://www.instagram.com/"):

            # Check if the link has already been posted and saved
            if user_post_url in post_urls:
                await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
                await update.message.reply_text(
                    "Post Link already saved. Choose start on the MENU to start the bot again.")
                return ConversationHandler.END
            else:

                
                post_urls.append(user_post_url)

                # Append the post URL to the list
                #post_urls.append(user_post_url)

                # Store the user and their linked Instagram post
                posts_liked = list(post_urls[0:(len(post_urls)-1)])
                print(f"Liked_Post: {posts_liked}")
                
                user_posts.setdefault(user_id, []).extend(posts_liked)

                await update.message.reply_text(
                    "Your Instagram post has been added successfully! Thank you for using BoostifyGrowth to boost your Instagram! \nSelect (/start) if you want to start again.")
                keyboard = [[InlineKeyboardButton("LIST 🗒", url=f"https://t.me/boost_upbot?start=start")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(chat_id=group_id, text=f'✅ {update.message.from_user.name} interacted with all of the posts.\n🖼 Check out their post : {user_post_url}',reply_markup=reply_markup)
                await asyncio.sleep(2)
                
                #user_post_url = ""
                
                await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        
                context.user_data['expected_post_url'] = False
                return ConversationHandler.END
            
        else:
            await update.message.reply_text("Invalid Instagram post URL. Please provide a valid link.")
            # Automatically delete the user's message if the URL is not valid
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            return ConversationHandler.END
    else:
        await update.message.reply_text("I'm not expecting an Instagram post URL right now.")
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        return ConversationHandler.END



async def help_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    message_text="""Welcome to Boostify Growth — Your Passport to Instagram Stardom! 🌟 
 
• HOW TO USE THE BOT?

1️⃣ — Click on the “LIST 🗒️” button to get started with the bot.
2️⃣ — Enter your Instagram username (eg; @monica). Make sure it’s valid and starts with ‘ @ ‘.
3️⃣ — Wait for a few seconds for the Bot to validate your IG account and save your username.
4️⃣ — Get the list of the posts that you have to like by using ‘ /posts_list ’.
5️⃣ — Make sure to engage with ALL the posts on your list. When done, use ‘ /send_mylink ‘ to send your IG post link you want to promote and get added to the list.
6️⃣ — Paste your IG post link and make sure it is in the right format: https://www.instagram.com/p/xxx . ANY OTHER LINKS BESIDES INSTAGRAM LINKS WILL BE AUTOMATICALLY REMOVED.
7️⃣ — Wait 1 minute for the bot to verify you engaged with all of the posts. If yes, your post link will be successfully added, OTHERWISE, IF YOU DON’T ENGAGE WITH ALL POSTS, YOU’LL BE WARNED.

You can use again the bot to add another post by repeating the same process.

• Ethical Rules:
1️⃣ — Any sender who promotes NSFW posts from Instagram will get a permanent ban.
2️⃣ — Any tentatives to use our services for business or profit, will get permanently banned and sued for Impersonation of our Services. 
3️⃣ — Any proof that indicates DM-ing our members for unreasonable motives such as: business, illegal activities and spamming, will be permanently Global Banned from all our groups.

Make sure to follow our rules and read our Terms and Conditions from our website.
Read more on our Official Channel: BOOSTIFY GROWTH. 

Happy Gaining! 😄"""
    keyboard = [[InlineKeyboardButton("TERMS AND CONDITIONS", url=f"https://boostifygrowth.tech/assets/bootstrap/terms")], [InlineKeyboardButton("WEBSITE", url=f"https://boostifygrowth.tech"), InlineKeyboardButton("CHANNEL", url=f"https://t.me/boostifygrowth")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup)

async def contact_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    message_text = "📥 Contact Boostify Growth — Contacting Options\n•Get in touch with our team if you have any issue & inquiry, by using the contact options listed below:"       
    keyboard = [[InlineKeyboardButton("E-MAIL 📧", url=f"https://boostifygrowth.tech/contacts"),InlineKeyboardButton("INSTAGRAM 📸", url=f"https://www.instagram.com/boostifygrowth")], [InlineKeyboardButton("TWITTER (X) 🐤", url=f"https://twitter.com/boostifygrowth"), InlineKeyboardButton("TELEGRAM ➤", url=f"https://t.me/boostifygrowth")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup)



async def error(update: Update, context: CallbackContext):
    try:
        print(f"Update {update} caused an error {context.error}")
    except Exception as e:
        print(f"An error occurred in the error handler: {e}")
    return OTHER_TEXT


def handle_responses(text: str) -> str:
    processed: str = text.lower()

    if "hello" in processed:
        return ("Hello there! Choose an option from the Menu.")
    
    if "how are you" in processed:
        return "I am good. How can I help you?"

    return "Choose a command from the menu"


async def handle_message(update:Update, context: ContextTypes.DEFAULT_TYPE):
    global user_post_url
    message_type: str = update.message.chat.type
    text: str = update.message.text    

    print(f"User ({update.message.chat.id}) in {message_type}: '{text}' ")
    
    if message_type == ("group") or message_type == ("supergroup"):

        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, " ").strip()
            response:str = handle_responses(new_text)
        else:
            return
    
    else:
        response: str = handle_responses(text)
    
    print("Bot: ", response)
    await context.bot.send_message(update.message.chat_id, response)
    return ConversationHandler.END

if __name__ == "__main__":
    print("Starting bot...")

    app = Application.builder().concurrent_updates(True).token(BOT_TOKEN).build()

    #Commands
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('contact', contact_command))
    app.add_handler(CommandHandler('posts_list',post_list))


    conv_handler = ConversationHandler(entry_points=[CommandHandler('start', start), CommandHandler('send_mylink', receive_instagram_post)],
                                       states={
                                           RECEIVE_USERNAME: [MessageHandler(filters.TEXT, receive_instagram_username)],
                                           CHECK_LIKE: [MessageHandler(filters.TEXT, Check_like)],
                                           OTHER_TEXT: [MessageHandler(filters.TEXT, handle_message)],
                                       },
                                       fallbacks=[]
                                       )
    app.add_handler(conv_handler)
    
    #errors
    app.add_error_handler(error)

    #polls the bot for new messages
    print("Polling...")
    app.run_polling(poll_interval=3) 
    
#await asyncio.run(multiple_Usage())

    #asyncio.run(multiple_Usage())
    # bot_thread = Thread(target=multiple_Usage)
    # bot_thread.start()
    # bot_thread.join()
