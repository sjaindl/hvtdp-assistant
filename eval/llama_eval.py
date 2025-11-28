import os

from llama_index.core import VectorStoreIndex
from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator

from engine.chat_engine import build_optimized_query_engine
from config import OPENAI_API_KEY
from llama_index.core.evaluation import RetrieverEvaluator


# from deepeval.integrations.llama_index import (
#     DeepEvalAnswerRelevancyEvaluator,
#     DeepEvalFaithfulnessEvaluator,
#     DeepEvalContextualRelevancyEvaluator,
#     DeepEvalSummarizationEvaluator,
#     DeepEvalBiasEvaluator,
#     DeepEvalToxicityEvaluator,
# )

# Path to your file inside the data dir
file_path = os.path.join("data", "output.txt")

# Make sure the data directory exists
os.makedirs("data", exist_ok=True)

# Clear the file on first launch
# (run this once at program start)
with open(file_path, "w") as f:
    f.write("")  # just clears the file

# Later in your code, append text
def log_text(text: str):
    with open(file_path, "a") as f:
        f.write(text + "\n")


def eval_faithfulness(vector_index: VectorStoreIndex):
    llm = OpenAI(model = "gpt-3.5-turbo", temperature = 0.0, api_key = OPENAI_API_KEY)
    #llm = Ollama(model="llama3.1:8b-instruct", request_timeout=120.0, temperature=0)
    #Settings.llm = llm

    # documents = load_api_endpoints(specs)
    # dataset_generator = RagDatasetGenerator.from_documents(
    #     documents = documents,
    #     llm = llm,
    #     num_questions_per_chunk = 1,  # set the number of questions per nodes
    # )

    #rag_dataset = dataset_generator.generate_questions_from_nodes()
    #questions = [e.query for e in rag_dataset.examples]
    questions = [
        "Wer ist im Meisterschaftskader vom HV TDP Stainz?",
        "Wieviel Trainingsbeteiligung hat Stefan Jaindl?",
        "Welche aktiven Mitglieder hat der HV TDP?",
        "Wer spielt alles als Verteidiger?",
        "Wieviele Matchballspenden an den Verein und von wem hat es gegeben?",
        "Welche Vereinsveranstaltungen hat es gegeben?",
        "Wieviel kosten 12 Entenlose?",
        "Wie kann ich den HV TDP kontaktieren?",
        "Stell mir eine Kollektion aus dem Fanshop des HV TDP für maximal € 100.- zusammen",
        "Gib mir die aktuelle Tabelle inkl. Anzahl der Siege, Niederlagen, Unentschieden, Punkte und Tordifferenz."
    ]

    for question in questions:
        #eval_query(vector_index, llm, question, True)
        eval_query(vector_index, llm, question, False)

    #query = "Wer ist im Meistschaftskader vom HV TDP Stainz?"


def eval_query(vector_index: VectorStoreIndex, llm: LLM, query: str, plain: bool):
    faithfulness_evaluator = FaithfulnessEvaluator(llm = llm)
    relevancy_evaluator = RelevancyEvaluator(llm = llm)
#    deep_eval_evaluator = DeepEvalAnswerRelevancyEvaluator()

    retriever = vector_index.as_retriever(similarity_top_k=2)
    retriever_evaluator = RetrieverEvaluator.from_metric_names(
        ["mrr", "hit_rate"], retriever= retriever
    )

    if plain:
        query_engine = vector_index.as_query_engine()
    else:
        query_engine = build_optimized_query_engine(vector_index)

    response = query_engine.query(query)
    metadata = response.metadata

    eval_result_faith = faithfulness_evaluator.evaluate_response(response = response)
    eval_result_rel = relevancy_evaluator.evaluate_response(query = query, response = response)

    # retr_eval_res = retriever_evaluator.evaluate(
    #     query="query",
    #     expected_ids=["node_id1", "node_id2"]
    # )
 #   evaluation_result = deep_eval_evaluator.evaluate_response(
   #     query = query, response = response
  #  )

    #print("Faithful: " + str(eval_result.passing))

    response_str = response.response
    print("Query: " + query)
    print("Response: " + response_str)
    print("Metadata" + str(metadata))
   # print("Retriever Res: " + str(retr_eval_res))
    print("Faithful: " + str(eval_result_faith.passing) + ", score: " + str(eval_result_faith.score))
    print("Relevant: " + str(eval_result_rel.passing) + ", score: " + str(eval_result_rel.score))

    with open("output.txt", "w") as f:
        log_text("Plain: " + str(plain))
        for item in response.metadata.items():
            log_text("Metadata: " + str(item))
       # log_text("Retriever Res: " + str(retr_eval_res))
        log_text("Query: " + query)
        log_text("Response: " + response_str)
        log_text("Faithful: " + str(eval_result_faith.passing) + ", score: " + str(eval_result_faith.score))
        log_text("Relevant: " + str(eval_result_rel.passing) + ", score: " + str(eval_result_rel.score))
        log_text("___________________________")

    # for source_node in response.source_nodes:
    #     eval_result = faithfulness_evaluator.evaluate(
    #         response = response_str, contexts = [source_node.get_content()]
    #     )
    #     print("Faithful: " + str(eval_result.passing) + ", score: " + str(eval_result.score))
    #
    #
    # for source_node in response.source_nodes:
    #     eval_result = relevancy_evaluator.evaluate(
    #         query = query,
    #         response = response_str,
    #         contexts = [source_node.get_content()],
    #     )
    #     print("Relevant: " + str(eval_result.passing) + ", score: " + str(eval_result.score))


