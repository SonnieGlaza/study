from aiogram.fsm.state import State, StatesGroup


class UserFlow(StatesGroup):
    testing = State()
    waiting_photo = State()
    waiting_consult_question = State()
