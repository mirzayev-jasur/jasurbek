from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- User Keyboards ---

# Main Menu Keyboard
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Asosiy menyu 🏠")],
        [KeyboardButton(text="Rasm yuborish 🖼️"), KeyboardButton(text="Video yuborish 🎬")],
        [KeyboardButton(text="Matnli xabar yuborish 📝"), KeyboardButton(text="Fayl yuborish 📁")],
        [KeyboardButton(text="Rezume yuklash 📄"), KeyboardButton(text="So'rov yuborish (savol) ❓")],
        [KeyboardButton(text="Biz bilan bog'lanish 📞"), KeyboardButton(text="Taklif yuborish 💡")],
        [KeyboardButton(text="Fikr bildirish 💬"), KeyboardButton(text="Ko'p beriladigan savollar ❓")],
        [KeyboardButton(text="Shaxsiy ma'lumotlarim 👤"), KeyboardButton(text="Statistika 📊")],
        [KeyboardButton(text="Rasmlar galereyasi 🏞️"), KeyboardButton(text="Video galereyasi 🎥")],
        [KeyboardButton(text="So'ngi yangiliklar 📰"), KeyboardButton(text="Telegram kanalingizga o'tish 🔗")],
        [KeyboardButton(text="Referal tizimi 🤝"), KeyboardButton(text="Promokod kiritish 🎁")],
        [KeyboardButton(text="Narxlar ro'yxati 💰"), KeyboardButton(text="Bepul xizmatlar ✅")],
        [KeyboardButton(text="Pullik xizmatlar 💳"), KeyboardButton(text="Adminga yozish ✍️")],
        [KeyboardButton(text="Shikoyat yuborish 🚨"), KeyboardButton(text="Tanishuv so'rovi yuborish 👋")],
        [KeyboardButton(text="Lokatsiya yuborish 📍"), KeyboardButton(text="Kontakt yuborish 📱")],
        [KeyboardButton(text="Ilova bog'lash / qo'llab-quvvatlash 🛠️")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Keyboard for sharing contact
contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Telefon raqamimni ulashish 📱", request_contact=True)],
        [KeyboardButton(text="Bekor qilish ❌")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Keyboard for sharing location
location_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Manzilimni ulashish 📍", request_location=True)],
        [KeyboardButton(text="Bekor qilish ❌")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Cancel keyboard
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Bekor qilish ❌")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Inline keyboard for "Ortga" and "Bosh menyu"
back_to_main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Ortga", callback_data="back"),
            InlineKeyboardButton(text="🔝 Bosh menyu", callback_data="main_menu")
        ]
    ]
)

# --- Admin Keyboards ---

# Admin Menu Keyboard
admin_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Barcha foydalanuvchilarni ko'rish 👥")],
        [KeyboardButton(text="Har bir foydalanuvchiga yozish ✍️")],
        [KeyboardButton(text="Foydalanuvchi statistikasi 📊")],
        [KeyboardButton(text="Xabar yuborish (broadcast) 📢")],
        [KeyboardButton(text="Tugma yaratish (custom keyboard) ⌨️")],
        [KeyboardButton(text="Rasm/video/fayl joylash ➕")],
        [KeyboardButton(text="Promokodlar yaratish 🎫")],
        [KeyboardButton(text="To'lovlar nazorati (optional) 💳")],
        [KeyboardButton(text="Fikrlar ko'rish 👁️")],
        [KeyboardButton(text="Takliflar ko'rish 💡")],
        [KeyboardButton(text="Shikoyatlar ko'rish 🚨")],
        [KeyboardButton(text="Savollar ko'rish ❓")],
        [KeyboardButton(text="Xatoliklarni ko'rish (logs) 📜")],
        [KeyboardButton(text="Admindan chiqish 🚪")],
        [KeyboardButton(text="Asosiy menyu 🏠")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# FAQ Inline Keyboard
faq_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Bot qanday ishlaydi?", callback_data="faq_how_works")],
        [InlineKeyboardButton(text="Qanday xizmatlar mavjud?", callback_data="faq_services")],
        [InlineKeyboardButton(text="Qo'llab-quvvatlash", callback_data="faq_support")],
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="main_menu")]
    ]
)
