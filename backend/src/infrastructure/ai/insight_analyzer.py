from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

class InsightAnalyzer:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model_name, temperature=0.3)
        self.prompt = ChatPromptTemplate.from_template("""
        You are a financial assistant. Analyze the following user transactions
        and provide a short insightful summary covering:
        - Total income vs expenses
        - Major spending categories
        - Unusual or high-value transactions
        - Suggested saving tips

        Transactions:
        {transactions}

        Provide a concise, user-friendly paragraph.
        """)
        self.parser = StrOutputParser()

    def analyze(self, transactions: list[dict]) -> str:
        tx_summary = "\n".join(
            [f"{t['tx_date']}: {t['description']} - {t['amount']} {t['currency']} ({t['transaction_type']})"
             for t in transactions]
        )
        chain = self.prompt | self.llm | self.parser
        return chain.invoke({"transactions": tx_summary})
