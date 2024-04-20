import requests
from textwrap import dedent
from memory import Memory

SYSTEM_PROMPT = """You are a {language} teacher named {teacher_name}, and you are a male. You are on a 1-on-1 
                   session with your  student, {user_name}, who is a {user_gender}. {user_name}'s {language} level 
                   is: {level}. Your task is to assist your student in advancing their {language}.
                   * When the session begins, offer a suitable session for {user_name}, unless asked for 
                   something else.
                   * {user_name}'s native language is {user_language}. {user_name} might address you in their own
                   language when felt their {language} is not well enough. When that happens, first translate their
                   message to {language}, and then reply.
                   * IMPORTANT: If your student makes any mistake, be it typo or grammar, you MUST first correct
                   your student and only then reply.
                   * You are only allowed to speak {language}."""

INITIAL_MESSAGE = """Greet me, and then suggest 3 optional subjects for our lesson suiting my level. 
                     You must reply in {language}."""

TUTOR_INSTRUCTIONS = """
                     ---
                     IMPORTANT: 
                     * If I replied in {language} and made any mistakes (grammar, typos, etc), you must correct me 
                     before replying
                     * You must keep the session flow, you're response cannot end the session. Try to avoid broad
                     questions like "what would you like to do", and prefer to provide me with related questions
                     and exercises. 
                     * You MUST reply in {language}.
                     """
memory = Memory()
history = memory.get_chat_history()
memory.add("system", dedent(SYSTEM_PROMPT.format(
            teacher_name='Alex', user_name='Duong', language='English', user_language='Vietnamese',
            level='beginers', user_gender='male'
        )))
if True:
     history.append({"role": "user", "content": dedent(INITIAL_MESSAGE.format(language='English'))})
else:
     history[-1]["content"] += dedent(TUTOR_INSTRUCTIONS.format(
        language=iso6391_to_language_name(self._language))
    )
# url = "https://chatgpt-42.p.rapidapi.com/gpt4"
url = "https://chat-gpt26.p.rapidapi.com/"
payload = { "model":"gpt-3.5-turbo","messages": history }
headers = {
	"content-type": "application/json",
	"Content-Type": "application/json",
	"X-RapidAPI-Key": "d4dfff94e5msha50c864b4ea5a16p1040b2jsn372c5801ef89",
	"X-RapidAPI-Host": "chat-gpt26.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())