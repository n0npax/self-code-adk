# self code adk

Agent which can read code of currently running application and help analyzing it. Its main purpose is to assist in debugging the whole application by enabling the agent, defined as a developer and multi-agent expert, to read the entire codebase.

## usage

### install the package

```sh
uv add self-code-adk
```
### import it

```python
from TODO_FIXME.agent import SelfCodeAgent
```

### And add new sub agent

```diff
+self_code_agent=SelfCodeAgent("gemini-2.5-flash-preview-04-17")
root_agent = Agent(
    name="my-fancy-agen",
    model="gemini-2.5-flash-preview-04-17",
    description=("root agent which acts as coordinator"),
    instruction=(
        """
        blah   
        """
    ),
+    sub_agents=[gardener, weather, self_code_agent],
-    sub_agents=[gardener, weather],
)```
