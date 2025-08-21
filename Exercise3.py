from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput, TResponseInputItem, InputGuardrailTripwireTriggered
from connection import config
import rich
from pydantic import BaseModel
import asyncio
from dotenv import load_dotenv

load_dotenv(".env")

# Define response model for GateKeeper
class GateKeeperResponse(BaseModel):
    message: str
    isOtherSchool: bool

# GateKeeper guardrail
@input_guardrail
async def gatekeeper_guardrail(ctx, agent: Agent, input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    # Extract input text
    if isinstance(input, list):
        user_input = input[0].text
    else:
        user_input = input

    # Define allowed school
    allowed_school = " Al-Anwar School"

    # Check if student is from another school
    is_other_school = allowed_school.lower() not in user_input.lower()

    response = GateKeeperResponse(
        message="🚫 Entry denied! Only students of  Al-Anwar School are allowed.",
        isOtherSchool=is_other_school,
    )

    rich.print(response)

    return GuardrailFunctionOutput(
        output_info=response,
        tripwire_triggered=is_other_school,
    )

# Define the GateKeeper Agent
gatekeeper_agent = Agent(
    name="Gate Keeper Agent",
    instructions="You are a strict gatekeeper. Allow only students of Al-Anwar School to enter.",
    input_guardrails=[gatekeeper_guardrail]
)

# Main runner
async def main():
    try:
        # Example 1: student from another school
        result = await Runner.run(
            gatekeeper_agent,
            "I am a student from Nationl School.",
            run_config=config,
        )
        rich.print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print("🚷 GateKeeper says: You cannot enter! You are not from Al-Anwar School.")

if __name__ == "__main__":
    asyncio.run(main())
