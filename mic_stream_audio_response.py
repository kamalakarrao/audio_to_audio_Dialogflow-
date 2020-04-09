# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Dialogflow API streams user input through the microphone and
speaks voice responses through the speaker.
Examples:
  python mic_stream_audio_response.py

  MAKE CHANGES IN 23RD LINE AND 246TH LINE
"""
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/path/to/file.json"  #Get the json key from service accounts   -- #https://dialogflow.com/docs/reference/v2-auth-setup
# [START dialogflow_microphone_streaming]
from gtts import gTTS

import dialogflow
from dialogflow import enums
import pyaudio
import simpleaudio as sa
import uuid
import json
from google.protobuf.json_format import MessageToJson
import time

# Audio recording parameters
SAMPLE_RATE = 44100  # Most modern mics support modeling at this rate
CHUNK_SIZE = int(SAMPLE_RATE / 10)


class Stream:
    """Start stream from microphone input to dialogflow API"""

    def __init__(self, project_id, session_id, language_code):
        self.project_id = project_id
        self.session_id = session_id
        self.language_code = language_code
        self.session_client = dialogflow.SessionsClient()
        self.final_request_received = False

    def _build_initial_request(self):
        """The first request should always contain the configuration"""
        session_path = self.session_client.session_path(
            project=self.project_id, session=self.session_id
        )

        input_audio_config = dialogflow.types.InputAudioConfig(
            audio_encoding=enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16,
            language_code=self.language_code,
            sample_rate_hertz=SAMPLE_RATE,
        )
        query_input = dialogflow.types.QueryInput(
            audio_config=input_audio_config
        )
        voice = dialogflow.types.VoiceSelectionParams(
            ssml_gender=enums.SsmlVoiceGender.SSML_VOICE_GENDER_FEMALE
        )
        speech_config = dialogflow.types.SynthesizeSpeechConfig(voice=voice)
        audio_encoding = (
            enums.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16
        )
        output_audio_config = dialogflow.types.OutputAudioConfig(
            audio_encoding=audio_encoding,
            sample_rate_hertz=SAMPLE_RATE,
            synthesize_speech_config=speech_config,
        )

        return dialogflow.types.StreamingDetectIntentRequest(
            session=session_path,
            query_input=query_input,
            output_audio_config=output_audio_config,
        )

    def _request_generator(self):
        """Get the audio from the microphone and build the request"""
        input_stream = pyaudio.PyAudio().open(
            channels=1, rate=SAMPLE_RATE, format=pyaudio.paInt16, input=True
        )

        yield self._build_initial_request()

        while True:
            if self.final_request_received:
                input_stream.close()
                return
            if input_stream.is_active():
                content = input_stream.read(
                    CHUNK_SIZE, exception_on_overflow=False
                )
                yield dialogflow.types.StreamingDetectIntentRequest(
                    input_audio=content
                )

    def stream(self):
        """Stream audio to Dialogflow and display the results"""
        while True:
            self.final_request_received = False
            print("=" * 20)
            requests = self._request_generator()
            responses = self.session_client.streaming_detect_intent(requests)
            #print(responses)

            for response in responses:

                if response.recognition_result.is_final:
                    #print(response)

                    print(
                        "\nFinal transcription: {}".format(
                            response.recognition_result.transcript
                        )
                    )
                    self.final_request_received = True
                elif not self.final_request_received:
                    #print(response)

                    print(
                        "Intermediate transcription: {}".format(
                            response.recognition_result.transcript
                        )
                    )
                if response.query_result.query_text:
                    # try:
                    #   print(response.query_result.parameters)
                    #   js_val = MessageToJson(response.query_result.parameters)  # str(response.query_result.parameters).replace("fields","")
                    #   js_v = json.loads(js_val)
                    #   if len(js_v['destination'])>2:
                    #     print("-----------")
                    #     print()
                    #     print(js_v['destination'])
                    #     print("-----------")
                    #     #text_to_speech("Destination as "+js_v['destination']+" is confirmed")
                    #     #time.sleep(20)
                    # except:
                    #      print("Error")
                    print(
                        "Fullfilment Text: {}".format(
                            response.query_result.fulfillment_text
                        )
                    )
                    print(
                        "Intent: {}".format(
                            response.query_result.intent.display_name
                        )
                    )
                if response.output_audio:
                    return response


def play_audio(audio):
    audio_obj = sa.play_buffer(audio, 1, 2, SAMPLE_RATE)
    audio_obj.wait_done()

def text_to_speech(mytext):
    language = 'en'

    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    myobj = gTTS(text=mytext, lang=language, slow=False)

    # Saving the converted audio in a mp3 file named
    # welcome
    myobj.save("welcome.mp3")
    #play_audio("welcome.mp3")
    #audio_obj = sa.WaveObject.from_wave_file("welcome.wav")
    #audio_obj.wait_done()
    # Playing the converted file
    os.system("mpg321 welcome.mp3")

# [START dialogflow_detect_intent_with_texttospeech_response]
def detect_intent_with_texttospeech_response(texts):
    """Returns the result of detect intent with texts as inputs and includes
    the response in an audio format.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    project_id = "printer-gbfmxs"
    session_id = uuid.uuid4()
    language_code = "en-US"
    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()

    session_path = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session_path))

    for text in texts:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)

        query_input = dialogflow.types.QueryInput(text=text_input)

        # Set the query parameters with sentiment analysis
        output_audio_config = dialogflow.types.OutputAudioConfig(
            audio_encoding=dialogflow.enums.OutputAudioEncoding
            .OUTPUT_AUDIO_ENCODING_LINEAR_16)

        response = session_client.detect_intent(
            session=session_path, query_input=query_input,
            output_audio_config=output_audio_config)

        print('=' * 20)
        print('Query text: {}'.format(response.query_result.query_text))
        print('Detected intent: {} (confidence: {})\n'.format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence))
        print('Fulfillment text: {}\n'.format(
            response.query_result.fulfillment_text))
        if response.output_audio:
            return response
        # The response's audio_content is binary.
        #with open('output.wav', 'wb') as out:
         #   out.write(response.output_audio)
          #  print('Audio content written to file "output.wav"')
# [END dialogflow_detect_intent_with_texttospeech_response]



def main(project_id, session_id, language_code):
    print('Listening...')
    while True:
      #if "y" == input("Press y to start"):
        #text_to_speech("Hello, How can i help?")
        try:
            response = Stream(project_id, session_id, language_code).stream()
            play_audio(response.output_audio)
        except Exception as e:
            print("Out of stream"+str(e))




if __name__ == "__main__":
    # TODO: developer replace these variables with your own
    project_id = "YOUR PROJECT ID"   #You can find them under dialogflow settings console
    session_id = str(uuid.uuid4())
    language_code = "en-US"
    main(project_id, session_id, language_code)
# [END dialogflow_microphone_streaming]
