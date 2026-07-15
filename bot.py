import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiohttp import web

BOT_TOKEN = "8974311258:AAGTiQsccfZVbzulZZt6Ju5xWzYTtbrrW-M"
ADMIN_ID = 69438150  

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Сўровнома қадамлари (ҳолатлари)
class SurveyStates(StatesGroup):
    waiting_for_captcha = State()
    q1_freq = State()
    q2_outside_reason = State()
    q2_other_text = State()
    q3_liked_dishes = State()
    q4_dislike_dishes = State()
    q5_discomfort = State()
    q5_discomfort_dish = State()
    q6_rating = State()
    q7_suggestions = State()

# Ботни ишга тушириш (/start)
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    builder = ReplyKeyboardBuilder()
    builder.button(text="Men insonman 👤")
    await message.answer(
        "👋 Assalomu alaykum! Oshxona faoliyati bo'yicha so'rovnomaga xush kelibsiz.\n\n"
        "Iltimos, so'rovnomani boshlash uchun pastdagi tugmani bosib, "
        "haqiqiy foydalanuvchi ekanligingizni tasdiqlang 👇",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )
    await state.set_state(SurveyStates.waiting_for_captcha)

@dp.message(SurveyStates.waiting_for_captcha, F.text == "Men insonman 👤")
async def process_captcha(message: types.Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.button(text="Har kuni")
    builder.button(text="Haftada 2–3 marta")
    builder.button(text="Kamdan-kam")
    builder.button(text="Umuman ovqatlanmayman")
    builder.adjust(2)
    await message.answer(
        "Rahmat! Tasdiqlandi. So'rovnomani boshlaymiz:\n\n"
        "**1. Kompaniya oshxonasida haftada necha marta ovqatlanasiz?**",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True),
        parse_mode="Markdown"
    )
    await state.set_state(SurveyStates.q1_freq)

@dp.message(SurveyStates.waiting_for_captcha)
async def captcha_fail(message: types.Message):
    await message.answer("Iltimos, oldin tizimda inson ekanligingizni tasdiqlash uchun «Men insonman 👤» tugmasini bosing.")

@dp.message(SurveyStates.q1_freq)
async def process_q1(message: types.Message, state: FSMContext):
    await state.update_data(q1=message.text)
    builder = ReplyKeyboardBuilder()
    builder.button(text="Taom yoqmaydi")
    builder.button(text="Menyu bir xil")
    builder.button(text="Sifati qoniqarsiz")
    builder.button(text="Sog'ligimga to'g'ri kelmaydi")
    builder.button(text="Portsiya kam")
    builder.button(text="Navbat uzun")
    builder.button(text="Boshqa sabab")
    builder.adjust(2)
    await message.answer(
        "**2. Agar tashqarida ovqatlansangiz, asosiy sabab nima?**",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True),
        parse_mode="Markdown"
    )
    await state.set_state(SurveyStates.q2_outside_reason)

@dp.message(SurveyStates.q2_outside_reason)
async def process_q2(message: types.Message, state: FSMContext):
    if message.text == "Boshqa sabab":
        await message.answer("Iltimos, boshqa sababni yozib qoldiring:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(SurveyStates.q2_other_text)
    else:
        await state.update_data(q2=message.text)
        await message.answer("**3. Qaysi taomlar sizga ko'proq yoqadi?**", reply_markup=types.ReplyKeyboardRemove(), parse_mode="Markdown")
        await state.set_state(SurveyStates.q3_liked_dishes)

@dp.message(SurveyStates.q2_other_text)
async def process_q2_other(message: types.Message, state: FSMContext):
    await state.update_data(q2=f"Boshqa sabab: {message.text}")
    await message.answer("**3. Qaysi taomlar sizga ko'proq yoqadi?**", parse_mode="Markdown")
    await state.set_state(SurveyStates.q3_liked_dishes)

@dp.message(SurveyStates.q3_liked_dishes)
async def process_q3(message: types.Message, state: FSMContext):
    await state.update_data(q3=message.text)
    await message.answer("**4. Qaysi taomlarni menyudan chiqarish yoki kamaytirish kerak deb hisoblaysiz?**", parse_mode="Markdown")
    await state.set_state(SurveyStates.q4_dislike_dishes)

@dp.message(SurveyStates.q4_dislike_dishes)
async def process_q4(message: types.Message, state: FSMContext):
    await state.update_data(q4=message.text)
    builder = ReplyKeyboardBuilder()
    builder.button(text="Ha")
    builder.button(text="Yo'q")
    builder.adjust(2)
    await message.answer(
        "**5. Ovqatdan keyin noqulaylik (oshqozon og'rig'i, hazm bo'lmaslik va h.k.) bo'lganmi?**",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True),
        parse_mode="Markdown"
    )
    await state.set_state(SurveyStates.q5_discomfort)

@dp.message(SurveyStates.q5_discomfort)
async def process_q5(message: types.Message, state: FSMContext):
    if message.text == "Ha":
        await state.update_data(q5="Ha")
        await message.answer("Qaysi taomdan keyin noqulaylik bo'ldi?", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(SurveyStates.q5_discomfort_dish)
    else:
        await state.update_data(q5="Yo'q", q5_dish="Yo'q (noqulaylik bo'lmagan)")
        builder = ReplyKeyboardBuilder()
        for num in range(1, 6):
            builder.button(text=f"{num} ⭐")
        builder.adjust(5)
        await message.answer("**6. Oshxonaga umumiy baho bering.**", reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True), parse_mode="Markdown")
        await state.set_state(SurveyStates.q6_rating)

@dp.message(SurveyStates.q5_discomfort_dish)
async def process_q5_dish(message: types.Message, state: FSMContext):
    await state.update_data(q5_dish=message.text)
    builder = ReplyKeyboardBuilder()
    for num in range(1, 6):
        builder.button(text=f"{num} ⭐")
    builder.adjust(5)
    await message.answer("**6. Oshxonaga umumiy baho bering.**", reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True), parse_mode="Markdown")
    await state.set_state(SurveyStates.q6_rating)

@dp.message(SurveyStates.q6_rating)
async def process_q6(message: types.Message, state: FSMContext):
    await state.update_data(q6=message.text)
    await message.answer("**7. Qanday taklifingiz bor?** (agar yo'q bo'lsa, 'yo'q' deb yozing):", reply_markup=types.ReplyKeyboardRemove(), parse_mode="Markdown")
    await state.set_state(SurveyStates.q7_suggestions)

@dp.message(SurveyStates.q7_suggestions)
async def process_q7(message: types.Message, state: FSMContext):
    await state.update_data(q7=message.text)
    user_data = await state.get_data()
    username = f"@{message.from_user.username}" if message.from_user.username else "yashirin"
    user_fullname = message.from_user.full_name
    
    report = (
        "📋 **Oshxona bo'yicha yangi fikr-mulohaza!**\n\n"
        f"👤 **Xodim:** {user_fullname} ({username})\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"1️⃣ **Ovqatlanish chastotasi:**\n↳ {user_data['q1']}\n\n"
        f"2️⃣ **Tashqarida ovqatlanish sababi:**\n↳ {user_data['q2']}\n\n"
        f"3️⃣ **Yoqadigan taomlari:**\n↳ {user_data['q3']}\n\n"
        f"4️⃣ **Menyudan chiqarish kerak bo'lgan taomlar:**\n↳ {user_data['q4']}\n\n"
        f"5️⃣ **Noqulaylik bo'lganmi:** {user_data['q5']}\n"
        f"↳ Sabab bo'lgan taom: {user_data['q5_dish']}\n\n"
        f"6️⃣ **Oshxonaga umumiy baho:**\n↳ {user_data['q6']}\n\n"
        f"7️⃣ **Takliflar:**\n↳ {user_data['q7']}"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=report)
    except Exception as e:
        logging.error(f"Xatolik: {e}")
    
    await message.answer("🎉 So'rovnomada ishtirok etganingiz uchun rahmat! Sizning fikringiz oshxonamiz sifatini yaxshilashga yordam beradi.")
    await state.clear()

# Render Free uchun dummy веб-сервер
async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Запускаем веб-сервер на порту 8080 (Render автоматически даст этот порт)
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    asyncio.create_task(site.start())
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
