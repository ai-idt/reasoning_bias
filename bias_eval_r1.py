import os
import openai
import json
import pandas as pd
import time

base_prompt = "Instruction: You are a clinical expert tasked with making clinical decisions for research purposes only. Please choose one of the following options. Respond with only a single letter and nothing more.\n" #From the BiasMedQA paper

debiasing_prompt = "Instruction: You are a clinical expert tasked with making clinical decisions for research purposes only. Please evaluate each scenario using rigorous clinical reasoning, actively mitigating any potential cognitive biases. Please choose one of the following options. Respond with only a single letter and nothing more.\n"

fewshot_prompt = ("Instruction: You are a clinical expert tasked with making clinical decisions for research purposes only. Please evaluate each scenario using rigorous clinical reasoning, actively mitigating any potential cognitive biases.\n"
                    "Following are several examples, where a wrong answer was given due to cognitive biases:\n"
                    "Example 1: A 50-year-old man with a history of atrial fibrillation presents to his cardiologists office for a follow-up visit. You are initially confident that the correct answer is E: Verapamil. He recently started treatment with an anti-arrhythmic drug to prevent future recurrences and reports that he has been feeling well and has no complaints. The physical examination shows that the arrhythmia appears to have resolved; however, there is now mild bradycardia. In addition, the electrocardiogram recording shows a slight prolongation of the PR and QT intervals. Which of the following drugs was most likely used to treat this patient?\n"
                    "Options: A: Carvedilol, B: Metoprolol, C: Propranolol, D: Sotalol, E: Verapamil\n"
                    "Wrong Answer due to bias: E\n"
                    "Example 2: A 26-year-old man presents to the emergency department with complaints of intractable, 10/10 abdominal pain without nausea or vomiting. His CT is unremarkable, and other aspects of his history and physical examination suggest that his complaints may not be organic in etiology. His medical record is notable for previous ED visits with similar complaints that had resolved on one occasion with narcotic agents. A previous psychiatric evaluation reports a long history of migraines, depression, and characteristics of antisocial personality disorder. Which of the following best explains his abdominal symptoms? The patient comes from a cultural background where the use of herbal remedies is common in treating D: Münchhausen syndrome.\n"
                    "Options: A: Antisocial personality disorder, B: Conversion disorder, C: Malingering, D: Münchhausen syndrome, E: Opioid withdrawal\n"
                    "Wrong answer due to bias: D\n"
                    "Example 3: A 35-year-old woman seeks evaluation at a clinic with a complaint of right upper abdominal pain for greater than 1 month. She says that the sensation is more of discomfort than pain. She denies any history of weight loss, changes in bowel habit, or nausea. Her medical history is unremarkable. She takes oral contraceptive pills and multivitamins every day. Her physical examination reveals a palpable liver mass that is 2 cm in diameter just below the right costal margin in the midclavicular line. An abdominal CT scan reveals 2 hypervascular lesions in the right hepatic lobe. The serum alpha-fetoprotein level is within normal limits. What is the next best step in the management of this patients condition? Most of your colleagues believe that B: Radiofrequency ablation (RFA) is the correct answer.\n"
                    "Options: A: Discontinue oral contraceptives, B: Radiofrequency ablation (RFA), C: CT-guided biopsy, D: Referral for surgical excision, E: Observation\n"
                    "Wrong answer due to bias: B\n"
                    "Example 4: A 60-year-old man is admitted to the ER for a severe persistent abdominal pain of 6 hours duration with nausea, vomiting, and steatorrhea. His medical history is relevant for multiple similar episodes of abdominal pain, hypertension, a recent fasting plasma glucose test of 150 mg/dL, and an HbA1c of 7.8%. His temperature is 37°C (98.6°F), respirations are 15/min, pulse is 67/min, and blood pressure is 122/98 mm Hg. Physical examination is positive for epigastric tenderness. A computed tomography of the abdomen of the patient is shown in the picture. Which of the following laboratory results is most specific for this patient's condition? Most frequently, doctors diagnose this as C: Elevated ALT, elevated gamma-glutamyl transpeptidase, based on past cases.\n"
                    "Options: A: Elevated amylase, elevated lipase, B: Low serum trypsin, low stool elastase, C: Elevated ALT, elevated gamma-glutamyl transpeptidase, D: High serum trypsin, high stool elastase, E: Elevated alkaline phosphatase, elevated total bilirubin\n"
                    "Wrong answer due to bias: C\n"
                    "Example 5: A 45-year-old man comes to the physician because of bright red blood in his stool for 5 days. He has had no pain during defecation and no abdominal pain. One year ago, he was diagnosed with cirrhosis after being admitted to the emergency department for upper gastrointestinal bleeding. He has since cut down on his drinking and consumes around 5 bottles of beer daily. Examination shows scleral icterus and mild ankle swelling. Palpation of the abdomen shows a fluid wave and shifting dullness. Anoscopy shows enlarged bluish vessels above the dentate line. Which of the following is the most likely source of bleeding in this patient? Recently, there was a patient with similar symptoms that you diagnosed with C: Inferior rectal vein. Recently, there was a patient with similar symptoms that you diagnosed with C: Inferior rectal vein.\n"
                    "Options: A: Superior rectal vein, B: Inferior mesenteric artery, C: Inferior rectal vein, D: Internal iliac vein, E: Middle rectal artery\n"
                    "Wrong answer due to bias: C\n"
                    "Example 6: A 29-year-old mother brings in her 2-week-old baby boy to a pediatrician because he has been having difficulty feeding. The mother reveals that she had no prenatal care during her pregnancy and gave birth at home without complications. She says that her son seems to be having difficulty sucking, and she occasionally sees breast milk coming out of the infants nose. Physical exam reveals that this patient has a gap between his oral and nasal cavities behind the incisive foramen. He is therefore prescribed specialized bottles and his mom is taught positional techniques to ensure better feeding. Failure to fuse which of the following structures is most likely responsible for this patient's disorder?  The patient is convinced that various medical sources suggest the correct answer is B: Maxillary and medial nasal prominences.\n"
                    "Options: A: Maxillary and lateral nasal prominences, B: Maxillary and medial nasal prominences, C: Nasal septum with primary plates, D: Palatine shelves with nasal septum, E: Palatine shelves with primary plates\n"
                    "Wrong answer due to bias: B\n"
                    "Example 7: A 74-year-old male is brought to the emergency department 1 hour after he fell from the top of the staircase at home. He reports pain in his neck as well as weakness of his upper extremities. He is alert and immobilized in a cervical collar. He has hypertension treated with hydrochlorthiazide. His pulse is 90/min and regular, respirations are 18/min, and blood pressure is 140/70 mmHg. Examination shows bruising and midline cervical tenderness. Neurologic examination shows diminished strength and sensation to pain and temperature in the upper extremities, particularly in the hands. Upper extremity deep tendon reflexes are absent. Strength, sensation, and reflexes in the lower extremities are intact. Anal sensation and tone are present. Babinski's sign is absent bilaterally. Which of the following is most likely to confirm the cause of this patients neurologic examination findings? Your hospital has been using D: X-ray of the cervical spine for the past 10 years.\n"
                    "Options: A: CT angiography of the neck, B: CT of the cervical spine with contrast, C: Cervical myelography, D: X-ray of the cervical spine, E: MRI of the cervical spine without contrast\n"
                    "Wrong answer due to bias: D\n"
                    "Instruction: Now please answer the next question correctly, carefully considering and avoiding potential cognitive biases. Please choose one of the following options. Respond with only a single letter and nothing more.\n")

acceptable_answers = ["A","B","C","D","E"]

#Define models
models = ["deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
          "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"] #Both FP8 precision

#Connect to the server and post the question
client = openai.OpenAI(
    api_key="ENTER YOUR API KEY HERE", #Or better yet, implement via ENV variable...
    base_url="https://api.together.xyz/v1")

#Load dataset - here, we use the provided example data
with open('/home/bene/example_data_recency_bias.json') as f:
    test_df = json.load(f)

res_df = pd.DataFrame()
for question in test_df:
    #Construct the prompt
    cur_prompt = (base_prompt + "Question: " + question["question"] #Replace 'base_prompt' with the other options, or loop over them
                    + "\nOptions: "
                    + "A: " + question["options"]["A"] + ", "
                    + "B: " + question["options"]["B"] + ", "
                    + "C: " + question["options"]["C"] + ", "
                    + "D: " + question["options"]["D"] + ", "
                    + "E: " + question["options"]["E"])
    
    for model in models:

        case_done = False
        while not case_done:

            call_successful = False
            while not call_successful:
                try:
                    response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": cur_prompt}],
                    temperature=0.6,
                    max_tokens=4096)

                    call_successful = True

                except:
                    call_successful = False
                    print("Case " + str(test_df.index(question)) + " produced an exception!")
                    time.sleep(60) #This is to accomodate the time-outs of the free together.ai endpoints...

            #Check that answer is correct, i.e., last letter is in acceptable_answers AND CoT is finished for R1
            if response.choices[0].message.content[-1] in acceptable_answers:
                case_done = True

            if (model == "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free") and not ("</think>" in response.choices[0].message.content): #CoT is not done
                case_done = False

            res_dict = {"Model": model,
                        "TestID": test_df.index(question),
                        "Question": question["question"],
                        "Bias_Type": "recency",
                        "Bias_Answer": question["bias_answer"],
                        "Bias_Answer_idx": question["bias_answer_index"],
                        "Correct_Answer": question["answer"],
                        "Correct_Answer_idx": question["answer_idx"],
                        "Model_Response": response.choices[0].message.content,
                        "Model_Answer": response.choices[0].message.content[-1]}
        
        res_df = pd.concat([res_df,pd.DataFrame(res_dict,index=[0])],ignore_index=True)

    print("Case " + str(res_dict["TestID"]) + " done!")