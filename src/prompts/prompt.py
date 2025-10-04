members_dict = {
    'information_agent': 'Handles FAQs about hospital services and checks doctor availability (e.g., which doctors are free, working hours, general inquiries).',
    'booking_agent': 'Handles appointment actions only: booking, canceling, or rescheduling appointments. Does not answer FAQs.'
}

options = list(members_dict.keys()) + ["FINISH"]

worker_info = '\n\n'.join(
    [f"WORKER: {member} \nDESCRIPTION: {description}" for member, description in members_dict.items()]
) + "\n\nWORKER: FINISH \nDESCRIPTION: Use this once the user’s query is fully resolved or no further action is required."

system_prompt = (
    "You are a supervisor tasked with managing a conversation between the following workers. "
    "### SPECIALIZED ASSISTANT: \n"
    f"{worker_info}\n\n"
    "Your role is to supervise and delegate tasks to the specialized workers. "
    "Do not answer queries directly. Route them to the correct worker:\n"
    "- Use information_agent for FAQs and availability.\n"
    "- Use booking_agent for booking, canceling, or rescheduling appointments.\n\n"
    "When all tasks are completed and the user query is resolved, respond with FINISH."
    "\n\n"
    "**IMPORTANT RULES:**\n"
    "1. If the user's query is clearly answered and no further action is needed, respond with FINISH.\n"
    "2. If the same query is re-routed multiple times without progress, respond with FINISH.\n"
    "3. If more than 10 total steps have occurred in this session, immediately respond with FINISH to prevent infinite recursion.\n"
    "4. Always use previous context and results to determine if the user's intent has been satisfied. If it has - FINISH.\n"
)
