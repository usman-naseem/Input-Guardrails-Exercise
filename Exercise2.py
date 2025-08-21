from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput, TResponseInputItem, InputGuardrailTripwireTriggered
from connection import config
import rich
from pydantic import BaseModel
import asyncio
from dotenv import load_dotenv

load_dotenv(".env")

# Define response model for father
class FatherResponse(BaseModel):
    message: str
    isTooCold: bool

# Father guardrail
@input_guardrail
async def father_guardrail(ctx, agent: Agent, input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    # Extract input text
    if isinstance(input, list):
        user_input = input[0].text
    else:
        user_input = input

    # Convert temperature if mentioned
    try:
        temp = int(user_input.strip().replace("C", "").replace("c", ""))
    except:
        temp = None

    # Check condition: stop running if below 26C
    is_too_cold = temp is not None and temp < 26

    response = FatherResponse(
        message="⚠️ It's too cold, don't go running below 26°C!",
        isTooCold=is_too_cold,
    )

    rich.print(response)

    return GuardrailFunctionOutput(
        output_info=response,
        tripwire_triggered=is_too_cold,
    )

# Define the Father Agent
father_agent = Agent(
    name="Father Agent",
    instructions="You are a caring father, advising your child about safe conditions for running.",
    input_guardrails=[father_guardrail]
)

# Main runner
async def main():
    try:
        # Example: child wants to run at 24C
        result = await Runner.run(
            father_agent,
            "24C",
            run_config=config,
        )
        rich.print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print("🚫 Father says: No running, it's below 26°C!")

if __name__ == "__main__":
    asyncio.run(main())
