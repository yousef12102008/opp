import telebot
import json
import os

# استبدل هذا بالتوكن الخاص بك
TOKEN = '6848019028:AAGDVZ4MIlMKOL0pRjtjMOadz4qkf9cqarU'
bot = telebot.TeleBot(TOKEN)

# معرف المسؤول (يمكنك إضافة المزيد من المعرفات في القائمة)
ADMINS = [6309252183]  # استبدل هذا بمعرف المسؤول الخاص بك

# تحميل البيانات من ملفات JSON
def load_json(filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []
    else:
        return []

# حفظ البيانات إلى ملفات JSON
def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)

# قائمة المستخدمين المصرح لهم
authorized_users = load_json('authorized_users.json')
# قائمة المستخدمين المكتومين
muted_users = load_json('muted_users.json')
# قائمة المستخدمين المحظورين
banned_users = load_json('banned_users.json')

# تحقق من أن المستخدم مصرح له
def is_user_authorized(user_id):
    return user_id in authorized_users

# تحقق من أن المستخدم مكتوم
def is_user_muted(user_id):
    return user_id in muted_users

# تحقق من أن المستخدم محظور
def is_user_banned(user_id):
    return user_id in banned_users

# تحقق من أن المستخدم مسؤول
def is_user_admin(user_id):
    return user_id in ADMINS

# استخراج معرف المستخدم من الرد
def extract_user_id_from_reply(message):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id
    return None

# أمر لإضافة مستخدم
@bot.message_handler(commands=['add'])
def add_user(message):
    if is_user_admin(message.from_user.id):
        user_id = extract_user_id_from_reply(message)
        if user_id:
            if user_id not in authorized_users:
                authorized_users.append(user_id)
                save_json(authorized_users, 'authorized_users.json')
                bot.reply_to(message, "User added successfully!")
            else:
                bot.reply_to(message, "User already authorized.")
        else:
            bot.reply_to(message, "Please reply to a user's message to add them.")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# أمر لكتم المستخدم
@bot.message_handler(commands=['mute'])
def mute_user(message):
    if is_user_admin(message.from_user.id):
        user_id = extract_user_id_from_reply(message)
        if user_id:
            try:
                bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=False)
                if user_id not in muted_users:
                    muted_users.append(user_id)
                    save_json(muted_users, 'muted_users.json')
                bot.reply_to(message, "User muted successfully!")
            except Exception as e:
                bot.reply_to(message, f"Failed to mute user: {str(e)}")
        else:
            bot.reply_to(message, "Please reply to a user's message to mute them.")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# أمر لحظر المستخدم
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if is_user_admin(message.from_user.id):
        user_id = extract_user_id_from_reply(message)
        if user_id:
            try:
                bot.kick_chat_member(message.chat.id, user_id)
                if user_id not in banned_users:
                    banned_users.append(user_id)
                    save_json(banned_users, 'banned_users.json')
                bot.reply_to(message, "User banned successfully!")
            except Exception as e:
                bot.reply_to(message, f"Failed to ban user: {str(e)}")
        else:
            bot.reply_to(message, "Please reply to a user's message to ban them.")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# أمر لإلغاء كتم المستخدم
@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if is_user_admin(message.from_user.id):
        user_id = extract_user_id_from_reply(message)
        if user_id:
            try:
                bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=True)
                if user_id in muted_users:
                    muted_users.remove(user_id)
                    save_json(muted_users, 'muted_users.json')
                bot.reply_to(message, "User unmuted successfully!")
            except Exception as e:
                bot.reply_to(message, f"Failed to unmute user: {str(e)}")
        else:
            bot.reply_to(message, "Please reply to a user's message to unmute them.")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# أمر لإلغاء حظر المستخدم
@bot.message_handler(commands=['unban'])
def unban_user(message):
    if is_user_admin(message.from_user.id):
        user_id = extract_user_id_from_reply(message)
        if user_id:
            try:
                bot.unban_chat_member(message.chat.id, user_id)
                if user_id in banned_users:
                    banned_users.remove(user_id)
                    save_json(banned_users, 'banned_users.json')
                bot.reply_to(message, "User unbanned successfully!")
            except Exception as e:
                bot.reply_to(message, f"Failed to unban user: {str(e)}")
        else:
            bot.reply_to(message, "Please reply to a user's message to unban them.")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# أمر لإيقاف البوت
@bot.message_handler(commands=['stop'])
def stop_bot(message):
    if is_user_admin(message.from_user.id):
        bot.reply_to(message, "Bot is stopping...")
        bot.stop_polling()

# أمر للتحقق من صلاحيات المستخدم
@bot.message_handler(commands=['check'])
def check_user(message):
    if is_user_authorized(message.from_user.id):
        bot.reply_to(message, "You are authorized!")
    else:
        bot.reply_to(message, "You are not authorized.")

# أمر لعرض قائمة الأوامر
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = "Available commands:\n"
    if is_user_admin(message.from_user.id):
        help_text += """
        /add - Add a user (reply to the user's message)
        /mute - Mute a user (reply to the user's message)
        /unmute - Unmute a user (reply to the user's message)
        /ban - Ban a user (reply to the user's message)
        /unban - Unban a user (reply to the user's message)
        /stop - Stop the bot
        """
    if is_user_authorized(message.from_user.id):
        help_text += """
        /check - Check if you are authorized
        """
    help_text += "/help - Show this help message\n"
    bot.reply_to(message, help_text)

# أوامر افتراضية
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if is_user_banned(message.from_user.id):
        return  # تجاهل الرسائل من المستخدمين المحظورين
    if is_user_muted(message.from_user.id):
        bot.reply_to(message, "You are muted.")
    elif is_user_authorized(message.from_user.id):
        # يمكن معالجة الرسائل الأخرى هنا إذا كنت ترغب في ذلك
        pass
    else:
        # لا تقم بالرد إذا لم يكن المستخدم مصرحًا له
        return

bot.polling()
