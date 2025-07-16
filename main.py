import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID, ADMIN_PASSWORD, DB_NAME, MEDIA_DIR, CHANNEL_ID
from database import Database
from keyboards import (
    main_menu_keyboard,
    contact_keyboard,
    location_keyboard,
    back_to_main_menu_keyboard,
    admin_menu_keyboard,
    cancel_keyboard,
    faq_keyboard
)
from states import UserStates, AdminStates

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize bot and dispatcher
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
db = Database(DB_NAME)


# --- Helper Functions ---

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID and db.is_admin_logged_in(user_id)


async def send_to_admin(message_text: str, from_user_id: int = None):
    """Send message to admin"""
    try:
        if from_user_id:
            user_data = db.get_user(from_user_id)
            if user_data:
                username = user_data[2] or "Mavjud emas"
                first_name = user_data[3] or "Mavjud emas"
                text = f"<b>Yangi xabar:</b>\n\n{message_text}\n\n<b>Yuboruvchi:</b>\n👤 {first_name}\n🆔 @{username}\n🔢 ID: {from_user_id}"
            else:
                text = f"<b>Yangi xabar:</b>\n\n{message_text}\n\n<b>Yuboruvchi ID:</b> {from_user_id}"
        else:
            text = message_text

        await bot.send_message(ADMIN_ID, text)
        return True
    except Exception as e:
        logging.error(f"Error sending message to admin: {e}")
        return False


# --- Start and Basic Handlers ---

@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    added = db.add_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_bot=user.is_bot,
        language_code=user.language_code
    )

    welcome_text = f"Assalomu alaykum, {user.full_name}! 🎉\n\n"
    if added:
        welcome_text += "Botimizga xush kelibsiz!\n"
    else:
        welcome_text += "Qaytganingizdan xursandmiz!\n"

    welcome_text += "Sizga qanday yordam bera olaman? Quyidagi tugmalardan birini tanlang:"

    await message.answer(welcome_text, reply_markup=main_menu_keyboard)
    db.add_message(user_id=user.id, message_text=message.text, message_type='text')


@router.message(F.text == "Asosiy menyu 🏠")
async def main_menu_handler(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Asosiy menyu:", reply_markup=main_menu_keyboard)


@router.message(F.text == "Bekor qilish ❌")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Amal bekor qilindi. Asosiy menyuga qaytdingiz.", reply_markup=main_menu_keyboard)


# --- User Message Handlers ---

@router.message(F.text == "Matnli xabar yuborish 📝")
async def send_text_message_prompt(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Iltimos, yubormoqchi bo'lgan matningizni kiriting:", reply_markup=cancel_keyboard)
    await state.set_state(UserStates.waiting_for_text_message)


@router.message(UserStates.waiting_for_text_message)
async def process_text_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')

    # Send to admin
    await send_to_admin(f"Matnli xabar: {message.text}", user_id)

    await message.answer("Matnli xabaringiz qabul qilindi va adminga yuborildi! ✅", reply_markup=main_menu_keyboard)
    await state.clear()


@router.message(F.text == "Rasm yuborish 🖼️")
async def request_photo(message: Message):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Iltimos, rasm yuboring:", reply_markup=cancel_keyboard)


@router.message(F.photo)
async def photo_message_handler(message: Message):
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id
    caption = message.caption or "Rasm"

    db.add_message(user_id=user_id, message_text=caption, message_type='photo', file_id=file_id)

    # Forward to admin
    try:
        await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        await send_to_admin(f"Yangi rasm yuborildi. Caption: {caption}", user_id)
    except Exception as e:
        logging.error(f"Error forwarding photo to admin: {e}")

    await message.answer("Rasm qabul qilindi va adminga yuborildi! ✅", reply_markup=main_menu_keyboard)


@router.message(F.text == "Video yuborish 🎬")
async def request_video(message: Message):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Iltimos, video yuboring:", reply_markup=cancel_keyboard)


@router.message(F.video)
async def video_message_handler(message: Message):
    user_id = message.from_user.id
    file_id = message.video.file_id
    caption = message.caption or "Video"

    db.add_message(user_id=user_id, message_text=caption, message_type='video', file_id=file_id)

    # Forward to admin
    try:
        await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        await send_to_admin(f"Yangi video yuborildi. Caption: {caption}", user_id)
    except Exception as e:
        logging.error(f"Error forwarding video to admin: {e}")

    await message.answer("Video qabul qilindi va adminga yuborildi! ✅", reply_markup=main_menu_keyboard)


@router.message(F.text == "Fayl yuborish 📁")
async def request_document(message: Message):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Iltimos, fayl yuboring:", reply_markup=cancel_keyboard)


@router.message(F.document)
async def document_message_handler(message: Message):
    user_id = message.from_user.id
    file_id = message.document.file_id
    file_name = message.document.file_name or "Fayl"

    db.add_message(user_id=user_id, message_text=file_name, message_type='document', file_id=file_id)

    # Forward to admin
    try:
        await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        await send_to_admin(f"Yangi fayl yuborildi: {file_name}", user_id)
    except Exception as e:
        logging.error(f"Error forwarding document to admin: {e}")

    await message.answer("Fayl qabul qilindi va adminga yuborildi! ✅", reply_markup=main_menu_keyboard)


# --- Contact and Location Handlers ---

@router.message(F.text == "Kontakt yuborish 📱")
async def request_contact_handler(message: Message):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Telefon raqamingizni ulashish uchun quyidagi tugmani bosing:", reply_markup=contact_keyboard)


@router.message(F.contact)
async def contact_shared_handler(message: Message):
    user_id = message.from_user.id
    contact = message.contact
    contact_info = f"Kontakt: {contact.phone_number}"

    db.add_message(user_id=user_id, message_text=contact_info, message_type='contact')

    # Send to admin
    await send_to_admin(f"Yangi kontakt: {contact.first_name} {contact.last_name or ''} - {contact.phone_number}",
                        user_id)

    await message.answer(
        f"Rahmat, {contact.first_name} {contact.last_name or ''} ({contact.phone_number}) kontaktingiz qabul qilindi va adminga yuborildi! ✅",
        reply_markup=main_menu_keyboard
    )


@router.message(F.text == "Lokatsiya yuborish 📍")
async def request_location_handler(message: Message):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Manzilingizni ulashish uchun quyidagi tugmani bosing:", reply_markup=location_keyboard)


@router.message(F.location)
async def location_shared_handler(message: Message):
    user_id = message.from_user.id
    location = message.location
    location_info = f"Lokatsiya: Lat {location.latitude}, Lon {location.longitude}"

    db.add_message(user_id=user_id, message_text=location_info, message_type='location')

    # Send to admin
    await send_to_admin(f"Yangi lokatsiya: Lat {location.latitude}, Lon {location.longitude}", user_id)

    await message.answer("Rahmat, manzilingiz qabul qilindi va adminga yuborildi! ✅", reply_markup=main_menu_keyboard)


# --- Feedback, Suggestions, Complaints, Questions ---

@router.message(F.text == "Fikr bildirish 💬")
async def request_feedback(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Iltimos, fikringizni yozing:", reply_markup=cancel_keyboard)
    await state.set_state(UserStates.waiting_for_feedback)


@router.message(UserStates.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext):
    user_id = message.from_user.id
    feedback_text = message.text

    db.add_feedback(user_id, feedback_text)
    await send_to_admin(f"Yangi fikr: {feedback_text}", user_id)

    await message.answer("Fikringiz qabul qilindi! Rahmat! ✅", reply_markup=main_menu_keyboard)
    await state.clear()


@router.message(F.text == "Taklif yuborish 💡")
async def request_suggestion(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Iltimos, taklifingizni yozing:", reply_markup=cancel_keyboard)
    await state.set_state(UserStates.waiting_for_suggestion)


@router.message(UserStates.waiting_for_suggestion)
async def process_suggestion(message: Message, state: FSMContext):
    user_id = message.from_user.id
    suggestion_text = message.text

    db.add_suggestion(user_id, suggestion_text)
    await send_to_admin(f"Yangi taklif: {suggestion_text}", user_id)

    await message.answer("Taklifingiz qabul qilindi! Rahmat! ✅", reply_markup=main_menu_keyboard)
    await state.clear()


@router.message(F.text == "Shikoyat yuborish 🚨")
async def request_complaint(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Iltimos, shikoyatingizni yozing:", reply_markup=cancel_keyboard)
    await state.set_state(UserStates.waiting_for_complaint)


@router.message(UserStates.waiting_for_complaint)
async def process_complaint(message: Message, state: FSMContext):
    user_id = message.from_user.id
    complaint_text = message.text

    db.add_complaint(user_id, complaint_text)
    await send_to_admin(f"Yangi shikoyat: {complaint_text}", user_id)

    await message.answer("Shikoyatingiz qabul qilindi va ko'rib chiqiladi! ✅", reply_markup=main_menu_keyboard)
    await state.clear()


@router.message(F.text == "So'rov yuborish (savol) ❓")
async def request_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Iltimos, savolingizni yozing:", reply_markup=cancel_keyboard)
    await state.set_state(UserStates.waiting_for_question)


@router.message(UserStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    question_text = message.text

    db.add_question(user_id, question_text)
    await send_to_admin(f"Yangi savol: {question_text}", user_id)

    await message.answer("Savolingiz qabul qilindi va tez orada javob beriladi! ✅", reply_markup=main_menu_keyboard)
    await state.clear()


# --- User Info and Stats ---

@router.message(F.text == "Shaxsiy ma'lumotlarim 👤")
async def show_personal_info(message: Message):
    user_id = message.from_user.id
    user_data = db.get_user(user_id)
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')

    if user_data:
        _, telegram_id, username, first_name, last_name, _, _, added_at = user_data
        response = (
            f"<b>Sizning ma'lumotlaringiz:</b>\n\n"
            f"🆔 ID: <code>{telegram_id}</code>\n"
            f"👤 Username: @{username or 'Mavjud emas'}\n"
            f"📝 Ism: {first_name or 'Mavjud emas'}\n"
            f"📝 Familiya: {last_name or 'Mavjud emas'}\n"
            f"🗓️ Ro'yxatdan o'tgan sana: {added_at.split('.')[0]}"
        )
    else:
        response = "Ma'lumotlaringiz topilmadi."

    await message.answer(response, reply_markup=main_menu_keyboard)


@router.message(F.text == "Statistika 📊")
async def show_user_stats(message: Message):
    user_id = message.from_user.id
    total_users = len(db.get_all_users())
    user_message_count = db.get_user_message_count(user_id)
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')

    response = (
        f"<b>Bot statistikasi:</b>\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"💬 Siz yuborgan xabarlar soni: {user_message_count}"
    )
    await message.answer(response, reply_markup=main_menu_keyboard)


# --- FAQ and Other Features ---

@router.message(F.text == "Ko'p beriladigan savollar ❓")
async def show_faq(message: Message):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Ko'p beriladigan savollar:", reply_markup=faq_keyboard)


@router.callback_query(F.data.startswith("faq_"))
async def handle_faq_callback(callback: CallbackQuery):
    data = callback.data

    if data == "faq_how_works":
        text = "Bot qanday ishlaydi?\n\nBu bot orqali siz admin bilan bog'lanishingiz, rasm, video, fayl yuborishingiz va turli xil so'rovlar yuborishingiz mumkin."
    elif data == "faq_services":
        text = "Qanday xizmatlar mavjud?\n\n• Rasm/video/fayl yuborish\n• Matnli xabar yuborish\n• Fikr bildirish\n• Taklif yuborish\n• Shikoyat yuborish\n• Savol berish"
    elif data == "faq_support":
        text = "Qo'llab-quvvatlash\n\nAgar sizda qo'shimcha savollar bo'lsa, 'Adminga yozish' tugmasini bosing."
    else:
        text = "Noma'lum savol."

    await callback.message.edit_text(text, reply_markup=faq_keyboard)
    await callback.answer()


@router.message(F.text == "Promokod kiritish 🎁")
async def request_promocode(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer("Iltimos, promokodni kiriting:", reply_markup=cancel_keyboard)
    await state.set_state(UserStates.waiting_for_promocode)


@router.message(UserStates.waiting_for_promocode)
async def process_promocode(message: Message, state: FSMContext):
    user_id = message.from_user.id
    promocode = message.text.strip()

    promo_data = db.check_promocode(promocode)
    if promo_data:
        await message.answer(f"✅ Promokod '{promocode}' faollashtirildi!\n\n{promo_data[2]}",
                             reply_markup=main_menu_keyboard)
        await send_to_admin(f"Promokod ishlatildi: {promocode}", user_id)
    else:
        await message.answer("❌ Noto'g'ri promokod yoki promokod faol emas.", reply_markup=main_menu_keyboard)

    await state.clear()


@router.message(F.text == "Telegram kanalingizga o'tish 🔗")
async def go_to_channel(message: Message):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer(f"Bizning rasmiy kanalimiz: {CHANNEL_ID}", reply_markup=main_menu_keyboard)


# --- Admin Authentication ---

@router.message(Command("admin"))
async def admin_login_request(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')

    if user_id != ADMIN_ID:
        await message.answer("Siz admin emassiz. 🚫")
        return

    if db.is_admin_logged_in(user_id):
        await message.answer("Siz allaqachon admin panelida kirgansiz! 👑", reply_markup=admin_menu_keyboard)
        return

    await message.answer("Admin panelga kirish uchun parolni kiriting:", reply_markup=cancel_keyboard)
    await state.set_state(AdminStates.waiting_for_password)


@router.message(AdminStates.waiting_for_password)
async def process_admin_password(message: Message, state: FSMContext):
    user_id = message.from_user.id
    password = message.text.strip()

    if user_id != ADMIN_ID:
        await message.answer("Siz admin emassiz. 🚫")
        await state.clear()
        return

    if password == ADMIN_PASSWORD:
        db.set_admin_session(user_id, True)
        await message.answer("✅ Muvaffaqiyatli kirildi! Admin paneliga xush kelibsiz! 👑",
                             reply_markup=admin_menu_keyboard)
        await state.clear()
    else:
        await message.answer("❌ Noto'g'ri parol. Qaytadan urinib ko'ring:", reply_markup=cancel_keyboard)


@router.message(F.text == "Admindan chiqish 🚪")
async def admin_logout(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id != ADMIN_ID:
        await message.answer("Siz admin emassiz. 🚫")
        return

    db.set_admin_session(user_id, False)
    await state.clear()
    await message.answer("Admin paneldan chiqildi. Asosiy menyuga qaytdingiz.", reply_markup=main_menu_keyboard)


# --- Admin Panel Handlers ---

@router.message(F.text == "Barcha foydalanuvchilarni ko'rish 👥")
async def show_all_users_admin(message: Message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        return

    users = db.get_all_users()
    if users:
        response = "<b>Barcha foydalanuvchilar:</b>\n\n"
        for i, (u_id, username, first_name, last_name) in enumerate(users, 1):
            message_count = db.get_user_message_count(u_id)
            response += (
                f"{i}. 🆔 <code>{u_id}</code>\n"
                f"👤 @{username or 'Mavjud emas'}\n"
                f"📝 {first_name or 'Mavjud emas'} {last_name or ''}\n"
                f"💬 Xabarlar: {message_count}\n"
                f"{'─' * 20}\n"
            )

        # Split long messages
        if len(response) > 4000:
            parts = [response[i:i + 4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await message.answer(part, reply_markup=admin_menu_keyboard)
        else:
            await message.answer(response, reply_markup=admin_menu_keyboard)
    else:
        await message.answer("Hozircha hech qanday foydalanuvchi yo'q.", reply_markup=admin_menu_keyboard)


@router.message(F.text == "Foydalanuvchi statistikasi 📊")
async def admin_user_stats(message: Message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        return

    total_users = len(db.get_all_users())
    response = f"<b>Umumiy statistika:</b>\n\n👥 Jami foydalanuvchilar: {total_users}"
    await message.answer(response, reply_markup=admin_menu_keyboard)


@router.message(F.text == "Xabar yuborish (broadcast) 📢")
async def request_broadcast_message(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        return

    await message.answer("Barcha foydalanuvchilarga yuborish uchun xabarni kiriting:", reply_markup=cancel_keyboard)
    await state.set_state(AdminStates.waiting_for_broadcast_message)


@router.message(AdminStates.waiting_for_broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        await state.clear()
        return

    broadcast_text = message.text
    users = db.get_all_users()

    success_count = 0
    fail_count = 0

    await message.answer("Xabar yuborilmoqda...")

    for user_data in users:
        try:
            await bot.send_message(user_data[0], broadcast_text)
            success_count += 1
        except Exception as e:
            fail_count += 1
            logging.error(f"Failed to send broadcast to {user_data[0]}: {e}")

    result_text = (
        f"<b>Broadcast natijasi:</b>\n\n"
        f"✅ Muvaffaqiyatli: {success_count}\n"
        f"❌ Muvaffaqiyatsiz: {fail_count}\n"
        f"📊 Jami: {success_count + fail_count}"
    )

    await message.answer(result_text, reply_markup=admin_menu_keyboard)
    await state.clear()


@router.message(F.text == "Promokodlar yaratish 🎫")
async def request_promocode_creation(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        return

    await message.answer(
        "Yangi promokod yaratish uchun quyidagi formatda kiriting:\nKOD|TAVSIF\n\nMisol: YANGI2024|Yangi foydalanuvchilar uchun chegirma",
        reply_markup=cancel_keyboard)
    await state.set_state(AdminStates.waiting_for_promocode_creation)


@router.message(AdminStates.waiting_for_promocode_creation)
async def process_promocode_creation(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        await state.clear()
        return

    try:
        code, description = message.text.split('|', 1)
        code = code.strip()
        description = description.strip()

        if db.add_promocode(code, description):
            await message.answer(f"✅ Promokod '{code}' muvaffaqiyatli yaratildi!", reply_markup=admin_menu_keyboard)
        else:
            await message.answer("❌ Promokod yaratishda xatolik yuz berdi. Ehtimol bunday kod allaqachon mavjud.",
                                 reply_markup=admin_menu_keyboard)
    except ValueError:
        await message.answer("❌ Noto'g'ri format. Iltimos, KOD|TAVSIF formatida kiriting.",
                             reply_markup=admin_menu_keyboard)

    await state.clear()


@router.message(F.text == "Fikrlar ko'rish 👁️")
async def view_feedback_admin(message: Message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        return

    feedback_list = db.get_all_feedback()
    if feedback_list:
        response = "<b>Barcha fikrlar:</b>\n\n"
        for feedback, first_name, username, timestamp in feedback_list:
            response += f"👤 {first_name} (@{username or 'mavjud emas'})\n💬 {feedback}\n🕐 {timestamp}\n{'─' * 30}\n"

        if len(response) > 4000:
            parts = [response[i:i + 4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await message.answer(part, reply_markup=admin_menu_keyboard)
        else:
            await message.answer(response, reply_markup=admin_menu_keyboard)
    else:
        await message.answer("Hozircha hech qanday fikr yo'q.", reply_markup=admin_menu_keyboard)


@router.message(F.text == "Takliflar ko'rish 💡")
async def view_suggestions_admin(message: Message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        return

    suggestions_list = db.get_all_suggestions()
    if suggestions_list:
        response = "<b>Barcha takliflar:</b>\n\n"
        for suggestion, first_name, username, timestamp in suggestions_list:
            response += f"👤 {first_name} (@{username or 'mavjud emas'})\n💡 {suggestion}\n🕐 {timestamp}\n{'─' * 30}\n"

        if len(response) > 4000:
            parts = [response[i:i + 4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await message.answer(part, reply_markup=admin_menu_keyboard)
        else:
            await message.answer(response, reply_markup=admin_menu_keyboard)
    else:
        await message.answer("Hozircha hech qanday taklif yo'q.", reply_markup=admin_menu_keyboard)


@router.message(F.text == "Shikoyatlar ko'rish 🚨")
async def view_complaints_admin(message: Message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        return

    complaints_list = db.get_all_complaints()
    if complaints_list:
        response = "<b>Barcha shikoyatlar:</b>\n\n"
        for complaint, first_name, username, timestamp in complaints_list:
            response += f"👤 {first_name} (@{username or 'mavjud emas'})\n🚨 {complaint}\n🕐 {timestamp}\n{'─' * 30}\n"

        if len(response) > 4000:
            parts = [response[i:i + 4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await message.answer(part, reply_markup=admin_menu_keyboard)
        else:
            await message.answer(response, reply_markup=admin_menu_keyboard)
    else:
        await message.answer("Hozircha hech qanday shikoyat yo'q.", reply_markup=admin_menu_keyboard)


@router.message(F.text == "Savollar ko'rish ❓")
async def view_questions_admin(message: Message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        return

    questions_list = db.get_all_questions()
    if questions_list:
        response = "<b>Barcha savollar:</b>\n\n"
        for question, first_name, username, timestamp in questions_list:
            response += f"👤 {first_name} (@{username or 'mavjud emas'})\n❓ {question}\n🕐 {timestamp}\n{'─' * 30}\n"

        if len(response) > 4000:
            parts = [response[i:i + 4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await message.answer(part, reply_markup=admin_menu_keyboard)
        else:
            await message.answer(response, reply_markup=admin_menu_keyboard)
    else:
        await message.answer("Hozircha hech qanday savol yo'q.", reply_markup=admin_menu_keyboard)


# --- Callback Query Handlers ---

@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    db.add_message(user_id=user_id, message_text=callback.data, message_type='callback')
    await callback.message.edit_text("Asosiy menyu:")
    await callback.message.answer("Asosiy menyu:", reply_markup=main_menu_keyboard)
    await callback.answer()


@router.callback_query(F.data == "back")
async def callback_back(callback: CallbackQuery):
    user_id = callback.from_user.id
    db.add_message(user_id=user_id, message_text=callback.data, message_type='callback')
    await callback.message.edit_text("Asosiy menyu:")
    await callback.message.answer("Asosiy menyu:", reply_markup=main_menu_keyboard)
    await callback.answer()


# --- Placeholder handlers for remaining buttons ---

@router.message(F.text.in_([
    "Rezume yuklash 📄", "Biz bilan bog'lanish 📞", "Rasmlar galereyasi 🏞️",
    "Video galereyasi 🎥", "So'ngi yangiliklar 📰", "Referal tizimi 🤝",
    "Narxlar ro'yxati 💰", "Bepul xizmatlar ✅", "Pullik xizmatlar 💳",
    "Adminga yozish ✍️", "Tanishuv so'rovi yuborish 👋", "Ilova bog'lash / qo'llab-quvvatlash 🛠️"
]))
async def placeholder_handlers(message: Message):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')

    responses = {
        "Rezume yuklash 📄": "Rezume yuklash funksiyasi tez orada qo'shiladi.",
        "Biz bilan bog'lanish 📞": "Biz bilan bog'lanish:\n📞 Telefon: +998901234567\n📧 Email: info@example.com",
        "Rasmlar galereyasi 🏞️": "Rasmlar galereyasi tez orada qo'shiladi.",
        "Video galereyasi 🎥": "Video galereyasi tez orada qo'shiladi.",
        "So'ngi yangiliklar 📰": "So'ngi yangiliklar tez orada qo'shiladi.",
        "Referal tizimi 🤝": "Referal tizimi tez orada qo'shiladi.",
        "Narxlar ro'yxati 💰": "Narxlar ro'yxati tez orada qo'shiladi.",
        "Bepul xizmatlar ✅": "Bepul xizmatlar ro'yxati tez orada qo'shiladi.",
        "Pullik xizmatlar 💳": "Pullik xizmatlar ro'yxati tez orada qo'shiladi.",
        "Adminga yozish ✍️": "Adminga xabar yuborish uchun 'Matnli xabar yuborish' tugmasini ishlating.",
        "Tanishuv so'rovi yuborish 👋": "Tanishuv so'rovi funksiyasi tez orada qo'shiladi.",
        "Ilova bog'lash / qo'llab-quvvatlash 🛠️": "Qo'llab-quvvatlash xizmati tez orada qo'shiladi."
    }

    response = responses.get(message.text, "Bu funksiya hali ishlab chiqilmoqda.")
    await message.answer(response, reply_markup=main_menu_keyboard)


# --- Admin placeholder handlers ---

@router.message(F.text.in_([
    "Har bir foydalanuvchiga yozish ✍️", "Tugma yaratish (custom keyboard) ⌨️",
    "Rasm/video/fayl joylash ➕", "To'lovlar nazorati (optional) 💳", "Xatoliklarni ko'rish (logs) 📜"
]))
async def admin_placeholder_handlers(message: Message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Siz admin emassiz yoki tizimga kirmagansiz. 🚫")
        return

    responses = {
        "Har bir foydalanuvchiga yozish ✍️": "Individual xabar yuborish funksiyasi tez orada qo'shiladi.",
        "Tugma yaratish (custom keyboard) ⌨️": "Custom keyboard yaratish funksiyasi tez orada qo'shiladi.",
        "Rasm/video/fayl joylash ➕": "Media joylash funksiyasi tez orada qo'shiladi.",
        "To'lovlar nazorati (optional) 💳": "To'lovlar nazorati funksiyasi tez orada qo'shiladi.",
        "Xatoliklarni ko'rish (logs) 📜": "Loglarni ko'rish funksiyasi tez orada qo'shiladi."
    }

    response = responses.get(message.text, "Bu admin funksiyasi hali ishlab chiqilmoqda.")
    await message.answer(response, reply_markup=admin_menu_keyboard)


# --- Generic Text Message Handler (fallback) ---

@router.message(F.text)
async def generic_text_handler(message: Message):
    user_id = message.from_user.id
    db.add_message(user_id=user_id, message_text=message.text, message_type='text')
    await message.answer(
        "Kechirasiz, men bu xabarni tushunmadim. Iltimos, menyudagi tugmalardan foydalaning.",
        reply_markup=main_menu_keyboard
    )


# --- Startup and Shutdown Hooks ---

async def on_startup():
    logging.info("Bot is starting...")
    db.connect()
    db.create_tables()
    logging.info(f"Media directory: {MEDIA_DIR}")
    logging.info("Bot started successfully!")


async def on_shutdown():
    logging.info("Bot is shutting down...")
    db.close()
    logging.info("Database connection closed.")
    logging.info("Bot shut down successfully!")


# --- Main function to run the bot ---

async def main():
    dp.include_router(router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
