import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Токен ва ID аллақачон киритилган
BOT_TOKEN = "897"
ADMIN_ID = 69438150  

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Сўровнома қадамлари (ҳолатлари)
class SurveyStates(StatesGroup):
    waiting_for_captcha = State() # Инсон эканлигини текшириш
    q1_freq = State()             # 1-савол
    q2_outside_reason = State()   # 2-савол
    q2_other_text = State()       # 2-савол учун бошқа сабаб
    q3_liked_dishes = State()     # 3-савол
    q4_dislike_dishes = State()   # 4-савол
    q5_discomfort = State()       # 5-савол
    q5_discomfort_dish = State()  # 5-савол учун таом
    q6_rating = State()           # 6-савол (Баҳо)
    q7_suggestions = State()      # 7-савол (Таклифлар)

# Ботни ишга тушириш (/start)
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear() # Эски маълумотларни тозалаймиз
    
    # Инсон эканлигини тасдиқлаш тугмаси
    builder = ReplyKeyboardBuilder()
    builder.button(text="Мен инсонман 👤")
    
    await message.answer(
        "👋 Ассалому алайкум! Ошхона фаолияти бўйича сўровномага хуш келибсиз.\n\n"
        "Илтимос, сўровномани бошлаш учун пастдаги тугмани босиб, "
        "ҳақиқий фойдаланувчи эканлигингизни тасдиқланг 👇",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )
    await state.set_state(SurveyStates.waiting_for_captcha)

# Капчани текшириш ва 1-саволга ўтиш
@dp.message(SurveyStates.waiting_for_captcha, F.text == "Мен инсонман 👤")
async def process_captcha(message: types.Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.button(text="Ҳар куни")
    builder.button(text="Ҳафтада 2–3 марта")
    builder.button(text="Камдан-кам")
    builder.button(text="Умуман овқатланмайман")
    builder.adjust(2)
    
    await message.answer(
        "Раҳмат! Тасдиқланди. Сўровномани бошлаймиз:\n\n"
        "**1. Компания ошхонасида ҳафтада неча марта овқатланасиз?**",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True),
        parse_mode="Markdown"
    )
    await state.set_state(SurveyStates.q1_freq)

# Агар капча тугмасини босмасдан бошқа нарса ёзса
@dp.message(SurveyStates.waiting_for_captcha)
async def captcha_fail(message: types.Message):
    await message.answer("Илтимос, олдин тизимда инсон эканлигингизни тасдиқлаш учун «Мен инсонман 👤» тугмасини босинг.")

# 1-саволга жавоб олиш
@dp.message(SurveyStates.q1_freq)
async def process_q1(message: types.Message, state: FSMContext):
    await state.update_data(q1=message.text)
    
    builder = ReplyKeyboardBuilder()
    builder.button(text="Таом ёқмайди")
    builder.button(text="Меню бир хил")
    builder.button(text="Сифати қониқарсиз")
    builder.button(text="Соғлиғимга тўғри келмайди")
    builder.button(text="Порция кам")
    builder.button(text="Навбат узун")
    builder.button(text="Бошқа сабаб")
    builder.adjust(2)
    
    await message.answer(
        "**2. Агар ташқарида овқатлансангиз, асосий сабаб нима?**",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True),
        parse_mode="Markdown"
    )
    await state.set_state(SurveyStates.q2_outside_reason)

# 2-саволга жавоб олиш
@dp.message(SurveyStates.q2_outside_reason)
async def process_q2(message: types.Message, state: FSMContext):
    if message.text == "Бошқа сабаб":
        await message.answer(
            "Илтимос, бошқа сабабни ёзиб қолдиринг:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(SurveyStates.q2_other_text)
    else:
        await state.update_data(q2=message.text)
        await message.answer(
            "**3. Қайси таомлар сизга кўпроқ ёқади?**",
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        await state.set_state(SurveyStates.q3_liked_dishes)

# Бошқа сабаб ёзилганда қабул қилиш
@dp.message(SurveyStates.q2_other_text)
async def process_q2_other(message: types.Message, state: FSMContext):
    await state.update_data(q2=f"Бошқа сабаб: {message.text}")
    await message.answer(
        "**3. Қайси таомлар сизга кўпроқ ёқади?**",
        parse_mode="Markdown"
    )
    await state.set_state(SurveyStates.q3_liked_dishes)

# 3-саволга жавоб олиш
@dp.message(SurveyStates.q3_liked_dishes)
async def process_q3(message: types.Message, state: FSMContext):
    await state.update_data(q3=message.text)
    await message.answer(
        "**4. Қайси таомларни менюдан чиқариш ёки камайтириш керак деб ҳисоблайсиз?**",
        parse_mode="Markdown"
    )
    await state.set_state(SurveyStates.q4_dislike_dishes)

# 4-саволга жавоб олиш
@dp.message(SurveyStates.q4_dislike_dishes)
async def process_q4(message: types.Message, state: FSMContext):
    await state.update_data(q4=message.text)
    
    builder = ReplyKeyboardBuilder()
    builder.button(text="Ҳа")
    builder.button(text="Йўқ")
    builder.adjust(2)
    
    await message.answer(
        "**5. Овқатдан кейин ноқулайлик (ошқозон оғриғи, ҳазм бўлмаслик ва ҳ.к.) бўлганми?**",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True),
        parse_mode="Markdown"
    )
    await state.set_state(SurveyStates.q5_discomfort)

# 5-саволга жавоб олиш
@dp.message(SurveyStates.q5_discomfort)
async def process_q5(message: types.Message, state: FSMContext):
    if message.text == "Ҳа":
        await state.update_data(q5="Ҳа")
        await message.answer(
            "Қайси таомдан кейин ноқулайлик бўлди?",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(SurveyStates.q5_discomfort_dish)
    else:
        await state.update_data(q5="Йўқ", q5_dish="Йўқ (ноқулайлик бўлмаган)")
        
        builder = ReplyKeyboardBuilder()
        for num in range(1, 6):
            builder.button(text=f"{num} ⭐")
        builder.adjust(5)
        
        await message.answer(
            "**6. Ошхонага умумий баҳо беринг.**",
            reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True),
            parse_mode="Markdown"
        )
        await state.set_state(SurveyStates.q6_rating)

# 5-саволнинг қўшимча майдони
@dp.message(SurveyStates.q5_discomfort_dish)
async def process_q5_dish(message: types.Message, state: FSMContext):
    await state.update_data(q5_dish=message.text)
    
    builder = ReplyKeyboardBuilder()
    for num in range(1, 6):
        builder.button(text=f"{num} ⭐")
    builder.adjust(5)
    
    await message.answer(
        "**6. Ошхонага умумий баҳо беринг.**",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True),
        parse_mode="Markdown"
    )
    await state.set_state(SurveyStates.q6_rating)

# 6-саволга жавоб олиш
@dp.message(SurveyStates.q6_rating)
async def process_q6(message: types.Message, state: FSMContext):
    await state.update_data(q6=message.text)
    await message.answer(
        "**7. Қандай таклифингиз бор?** (агар йўқ бўлса, 'йўқ' деб ёзинг):",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(SurveyStates.q7_suggestions)

# Охирги жавоб ва ҳисоботни юбориш
@dp.message(SurveyStates.q7_suggestions)
async def process_q7(message: types.Message, state: FSMContext):
    await state.update_data(q7=message.text)
    user_data = await state.get_data()
    
    username = f"@{message.from_user.username}" if message.from_user.username else "яширин"
    user_fullname = message.from_user.full_name
    
    report = (
        "📋 **Ошхона бўйича янги фикр-мулоҳаза!**\n\n"
        f"👤 **Ходим:** {user_fullname} ({username})\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"1️⃣ **Овқатланиш частотаси:**\n↳ {user_data['q1']}\n\n"
        f"2️⃣ **Ташқарида овқатланиш сабаби:**\n↳ {user_data['q2']}\n\n"
        f"3️⃣ **Ёқадиган таомлари:**\n↳ {user_data['q3']}\n\n"
        f"4️⃣ **Менюдан чиқариш керак бўлган таомлар:**\n↳ {user_data['q4']}\n\n"
        f"5️⃣ **Ноқулайлик бўлганми:** {user_data['q5']}\n"
        f"↳ Сабаб бўлган таом: {user_data['q5_dish']}\n\n"
        f"6️⃣ **Ошхонага умумий баҳо:**\n↳ {user_data['q6']}\n\n"
        f"7️⃣ **Таклифлар:**\n↳ {user_data['q7']}"
    )
    
    # Ҳисоботни СИЗГА (ADMIN_ID) юбориш
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=report)
    except Exception as e:
        logging.error(f"Ҳисоботни юборишда хатолик юз берди: {e}")
    
    await message.answer("🎉 Сўровномада иштирок этганингиз учун раҳмат! Сизнинг фикрингиз ошхонамиз сифатини яхшилашга ёрдам беради.")
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())