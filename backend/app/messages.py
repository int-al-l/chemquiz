"""Every message the server shows a person, in English and Russian.

Values are filled with str.format: `text("name_too_long", "ru", n=20)`.
The English texts are the ones the site has always shown.
"""

from __future__ import annotations

MESSAGES: dict[str, dict[str, str]] = {
    # --- class game ---
    "game_started": {"en": "The game has already started", "ru": "Игра уже началась"},
    "need_player": {"en": "Wait for at least one player to join", "ru": "Дождитесь, пока подключится хотя бы один игрок"},
    "game_over": {"en": "The game is over", "ru": "Игра окончена"},
    "no_such_player": {"en": "No such player", "ru": "Такого игрока нет"},
    "game_finished": {"en": "This game has finished", "ru": "Эта игра уже закончилась"},
    "room_locked": {"en": "The host has locked this game", "ru": "Ведущий закрыл вход в игру"},
    "name_taken": {"en": "Someone already has that name -- pick another", "ru": "Такое имя уже занято — выберите другое"},
    "room_full": {"en": "The room is full", "ru": "В комнате нет мест"},
    "too_late": {"en": "Too late -- this question is closed", "ru": "Поздно — вопрос уже закрыт"},
    "not_open_yet": {"en": "Answers are not open yet", "ru": "Отвечать пока нельзя"},
    "already_answered": {"en": "You have already answered", "ru": "Вы уже ответили"},
    "not_an_option": {"en": "That is not one of the options", "ru": "Такого варианта нет"},
    "type_a_name": {"en": "Type a name", "ru": "Введите имя"},
    "name_too_long": {"en": "Names can be at most {n} characters", "ru": "Имя может быть не длиннее {n} символов"},
    "game_not_found": {"en": "No game with that PIN", "ru": "Игры с таким PIN нет"},
    "host_only": {"en": "Only the host can do that", "ru": "Это может только ведущий"},
    "no_items": {"en": "There are no items to ask about here", "ru": "Здесь нет карточек для вопросов"},
    "no_free_pins": {"en": "No free room codes right now", "ru": "Сейчас нет свободных кодов комнат"},
    "unknown_mode": {"en": "Unknown mode '{mode}'", "ru": "Неизвестный режим «{mode}»"},
    "bad_time_limit": {"en": "Unsupported time limit", "ru": "Такое время на вопрос не поддерживается"},
    "not_in_game": {"en": "You are not in this game", "ru": "Вы не участвуете в этой игре"},
    "removed_from_game": {"en": "The host removed you from this game", "ru": "Ведущий удалил вас из игры"},
    # --- past games ---
    "no_such_game": {"en": "No such game", "ru": "Такой игры нет"},
    "finish_first": {"en": "Finish the game first", "ru": "Сначала завершите игру"},
    "deck_gone": {"en": "That deck is no longer on the site", "ru": "Этой колоды больше нет на сайте"},
    "no_mistakes": {"en": "The class got every question right -- nothing to go over", "ru": "Класс ответил на все вопросы верно — повторять нечего"},
    "items_gone": {"en": "Those items are no longer on the site", "ru": "Этих карточек больше нет на сайте"},
    # --- content and quizzes ---
    "no_category": {"en": "No category '{slug}'", "ru": "Колоды «{slug}» нет"},
    "no_item": {"en": "No item '{slug}'", "ru": "Карточки «{slug}» нет"},
    "empty_category": {"en": "no items available for this category", "ru": "В этой колоде нет карточек"},
    "quiz_not_found": {"en": "Quiz not found or expired", "ru": "Квиз не найден или устарел"},
    "no_question": {"en": "Quiz has no question {position}", "ru": "В квизе нет вопроса {position}"},
    "question_answered": {"en": "Question already answered", "ru": "На этот вопрос уже ответили"},
    "choice_not_option": {"en": "choice_id is not one of this question's options", "ru": "Такого варианта нет в этом вопросе"},
    # --- accounts ---
    "sign_in_required": {"en": "Sign in to use your list.", "ru": "Войдите, чтобы пользоваться списком."},
    "sign_in_expired": {"en": "That sign-in has expired.", "ru": "Вход устарел — войдите снова."},
    "bad_email": {"en": "That does not look like an email address.", "ru": "Это не похоже на адрес почты."},
    "password_short": {"en": "Use at least {n} characters for the password.", "ru": "Пароль должен быть не короче {n} символов."},
    "password_weak": {"en": "Mix letters with numbers or symbols in the password.", "ru": "Добавьте в пароль цифры или символы, не только буквы."},
    "email_failed": {"en": "Could not send the email right now. Try again in a minute.", "ru": "Сейчас не получается отправить письмо. Попробуйте через минуту."},
    "bad_code": {"en": "That code is wrong or has expired.", "ru": "Код неверный или устарел."},
    "bad_link": {"en": "That link is no longer valid. Ask for a new one.", "ru": "Ссылка больше не действует. Запросите новую."},
    "code_missing": {"en": "Enter the code from the email.", "ru": "Введите код из письма."},
    "too_many_codes": {"en": "Too many wrong codes. Ask for a new email.", "ru": "Слишком много неверных кодов. Запросите новое письмо."},
    "name_missing": {"en": "Please enter a name.", "ru": "Введите имя."},
    "account_exists": {"en": "There is already an account with this email. Sign in instead.", "ru": "С этой почтой уже есть аккаунт. Войдите в него."},
    "account_needs_password": {"en": "This email already has an account. Use “Forgot password” to set a password.", "ru": "На эту почту уже есть аккаунт. Задайте пароль через «Забыли пароль?»."},
    "legacy_account": {"en": "This account was made before passwords existed. Use “Forgot password” to set one.", "ru": "Этот аккаунт создан до появления паролей. Задайте пароль через «Забыли пароль?»."},
    "wrong_password": {"en": "Wrong email or password.", "ru": "Неверная почта или пароль."},
    "verify_first": {"en": "Please verify your email first. We have sent you a new code.", "ru": "Сначала подтвердите почту. Мы отправили новый код."},
    "progress_too_large": {"en": "Progress document too large.", "ru": "Слишком большой файл прогресса."},
}


def text(key: str, lang: str, **values) -> str:
    texts = MESSAGES[key]
    return (texts.get(lang) or texts["en"]).format(**values)
