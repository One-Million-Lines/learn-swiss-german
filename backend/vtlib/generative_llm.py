import json
import os
import re

from yaml import tokens

from vtutils.vtlogger import getLog
from openai import APIError, APIConnectionError, APITimeoutError, OpenAIError, RateLimitError, PermissionDeniedError
import time

# from litellm import completion
# TODO > Remove this class and use generativeLLM2 with this name.



class GenerativeLLM(object):
    def __init__(self, openai_client, genai_client=None):
        self.openai_client = openai_client
        self.genai_client = genai_client    
        self.vtlog = getLog("genai")

    def call_openai_tools (self, message_list, tools_list=None, llm_model="gpt-4o-mini", temperature=0.1, response_format="json", retry_count=0, reasoning_effort=None):
        # self.vtlog.debug("openai_call", llm_model=llm_model, temperature=temperature, response_format=response_format, retry_count=retry_count)
        # make_openai_request
        # had "gpt-3.5-turbo" or "gpt-4o"
        if not llm_model:
            llm_model = "gpt-4o-mini"
        try:
            openai_params = {
                "model": llm_model,
                "messages": message_list
            } 
            # gpt-5 doesn't accept temperature
            if temperature is not None and not llm_model.startswith("gpt-5"):
                openai_params["temperature"] = temperature
            # we configure response_format
            if response_format == "json":
                openai_params["response_format"] = {"type": "json_object"}
            if tools_list:
                openai_params["tools"] = tools_list
                openai_params["tool_choice"] = "none"

            if llm_model.startswith("gpt-5") and reasoning_effort:
                openai_params["reasoning_effort"] = reasoning_effort

            response = self.openai_client.chat.completions.create(**openai_params)
            # we might have a problem from openai
            if not response:
                self.vtlog.error("no_response_from_openai",exc=exc, message_list=message_list[0]["content"])
                return None, {"tokens": 0}
            # it returns the content
            response_message = response.choices[0].message.content
            # print (response['usage']['total_tokens']) # prompt_tokens and completion_tokens available
            # add response.usage.total_tokens to the response
            if response_format == "json":
                try:
                    # simple cleaning of response_message. Sometimes this includes huge number of empty lines
                    s = re.sub(r"(?m)(?:\r?\n[ \t]*){3,}", "\n", response_message)
                    response_message = json.loads(s)
                except Exception as exc:
                    self.vtlog.error("no_valid_json_response", exc=exc, response_message=response_message)
            
            # we return response.usage.total_tokens
            tokens = getattr(response, "usage", None)
            total_tokens = getattr(tokens, "total_tokens", 0) if tokens else 0
            return response_message, {"tokens": total_tokens}
        
        except APIError as e:
            # This is the most common exception for API-related errors
            status_code = getattr(e, "status_code", None)
            if status_code is None:
                status_code = getattr(e, "code", None)
            error_message = getattr(e, "message", str(e))
            # retries for 500 errors max 3 times.
            if status_code == 500 and retry_count < 3:
                # Retry logic for 500 errors
                self.vtlog.debug(
                    "openai_api_retry",
                    status_code=status_code,
                    exc=e,
                    message_list=message_list[0]["content"][:100],
                    retry_count=retry_count
                )
                # some backoff
                time.sleep(2 ** retry_count)  # Exponential backoff
                return self.call_openai_tools(message_list, tools_list, llm_model, temperature, 
                                              response_format=response_format, retry_count=retry_count + 1)

            elif status_code == 400 and "context_length_exceeded" in e.message:
                # Handle 400 errors (Bad Request)
                pass

            # we log the errror
            self.vtlog.error(
                "openai_api_error",
                status_code=status_code,
                exc=e,
                message_list=message_list[0]["content"][:100]
            )
            # You can decide how to handle or re-raise the error here
            return None, {"tokens": 0, "error": f"API Error: {status_code} - {error_message}"}
        
        except APITimeoutError as e:
            # Specific error for timeouts
            self.vtlog.error(
                "openai_api_timeout",
                exc=e, # Timeout error might not have a status_code attribute directly
                message_list=message_list[0]["content"][:100]
            )
            return None, {"tokens": 0, "error": f"API Timeout: {e}"}

        except APIConnectionError as e:
            # Specific error for connection issues
            self.vtlog.error(
                "openai_api_connection_error",
                exc=e,
                message_list=message_list[0]["content"][:100]
            )
            return None, {"tokens": 0, "error": f"API Connection Error: {e}"}

        except Exception as e:
            # we only print first element from the list because it might be too long
            if "context_length_exceeded" in str(e):
                message_list[0]["content"] = message_list[0]["content"][:100]
            

            self.vtlog.error("openai_error", exc=e, msg_list=message_list[0])
            return None, {"tokens": 0}
    


    def get_embeddings(self, input_message, model="text-embedding-3-small"):
        try:
            # we replace new lines with space
            input_message = input_message.replace("\n", ' ').replace("\r", "")
            openai_params = {
                "model": model,
                "input": input_message,
                "encoding_format": "float"
            }
            response = self.openai_client.embeddings.create(**openai_params)
            # it returns the content
            return response.data[0].embedding

        except Exception as e:
            self.vtlog.error("openai_error", exc=e, input_data=input_message)
            return None
