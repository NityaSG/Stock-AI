import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


def generate(base64_image):
  vertexai.init(project="infra-vertex-408019", location="us-west1")
  model = GenerativeModel("gemini-1.0-pro-vision-001")
  image1 = Part.from_data(data=base64.b64decode(base64_image), mime_type="image/png")
  responses = model.generate_content(
    [image1, """Provide a detailed analysis of the stock\'s graph in the picture and let me know wheter should i buy this stock or not"""],
    generation_config={
        "max_output_tokens": 2048,
        "temperature": 1,
        "top_p": 1,
        "top_k": 32
    },
    safety_settings={
          generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
          generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
          generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
          generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    stream=True,
  )
  
   # Initialize an empty string to collect all responses
  analysis_text = ""
  for response in responses:
        analysis_text += response.text

    # Return the concatenated response texts
  return analysis_text
