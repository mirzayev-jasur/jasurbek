from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    waiting_for_text_message = State()
    waiting_for_feedback = State()
    waiting_for_suggestion = State()
    waiting_for_complaint = State()
    waiting_for_question = State()
    waiting_for_admin_message = State()
    waiting_for_promocode = State()

class AdminStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_broadcast_message = State()
    waiting_for_promocode_creation = State()
    waiting_for_user_id_message = State()
    waiting_for_individual_message = State()
