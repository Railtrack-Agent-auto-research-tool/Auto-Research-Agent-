import asyncio

from docuglean import parse_pdf
from txtmarker.factory import Factory

async def main():
    result = await parse_pdf(
        "C:\\Users\\dsouz\\Downloads\\A_Novel_Integrated_Approach_for_Stock_Prediction_Based_on_Modal_Decomposition_Technology_and_Machine_Learning.pdf")
    paragraphs = result["text"].split("\n\n")
    for i, paragraph in enumerate(paragraphs):
        print(f"{i}: {paragraph}")

async def main2():
    highlighter = Factory.create("pdf")
    highlights = [
        ("test","""After the COVID-19 ended, the global economy gradually recovered."""),
        ("","""The stock market plays a great role in the capital market,
which can promote capital flow, optimize asset allocation,
and stimulate better and faster economic development""")
    ]
    highlighter.highlight("C:\\Users\\dsouz\\Downloads\\A_Novel_Integrated_Approach_for_Stock_Prediction_Based_on_Modal_Decomposition_Technology_and_Machine_Learning.pdf","highlighted.pdf",highlights)


asyncio.run(main2())