from typing import List, Optional, Any

from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle

class BoostImportant(BaseNodePostprocessor):

    bonus: float = 0.0

    def __init__(self, /, bonus: float = 0.1, **data: Any):
        super().__init__(**data)
        self.bonus = bonus

    def _postprocess_nodes(self, nodes: List[NodeWithScore], query_bundle: Optional[QueryBundle] = None) -> List[NodeWithScore]:
        for node in nodes:
            score = node.score or 0.0
            if (node.node.metadata or {}).get("important") is True:
                score = min(score + self.bonus, 0.99)
            node.score = score
        nodes.sort(key = lambda x: x.score or 0.0, reverse = True)

        print(nodes[0].node.metadata)
        print(nodes[0].score)

        return nodes
