# Exposing the Fragility of LLM Reasoning Through Bias-Inducing Prompts – Evidence from BiasMedQA

**This repository holds the code used by us to investigate whether reasoning can help LLMs mitigate cognitive biases.**

![Study Overview](overview.png)

*Objectives:*  
To evaluate the robustness of LLMs with and without reasoning to cognitive biases.

*Methods and Analysis:*  
The performance of Llama-3.3-70B, Qwen3-32B, and Gemini-2.5-Flash along with their reasoning-enhanced variants, was evaluated in the public BiasMedQA dataset developed to evaluate seven established cognitive biases in 1,273 clinical case vignettes. Each model was tested using a base prompt, a debiasing prompt with the instruction to actively mitigate cognitive bias, and a few-shot prompt with additional sample cases of biased responses. Beyond the seven biases from BiasMedQA, Gemini-2.5-Flash was additionally tested using four unpublished bias-inducing prompts to unveil signs of potential data contamination and actively investigate brittleness. For each model pair, two mixed-effects logistic regression models were fitted to determine the impact of biases and mitigation strategies on performance. 

*Results:*  
In all three models, the reasoning-enhanced variant achieved higher rate of correct responses (Llama-3.3-70B: 72.5-82.1% vs. 61.0-73.4%, Qwen3-32B: 71.7-78.7% vs. 55.5-64.1%, Gemini-2.5-Flash: 81.8-88.6% vs. 80.0-83.7%). The performance of Gemini-2.5-Flash dropped considerably when exposing it to four additional unpublished bias-inducing prompts (from 80.0-88.6% to 47.4-86.1%), hinting at potential contamination of its training data and exposing underlying brittleness. 
In Llama-3.3-70B and Gemini-2.5-Flash, reasoning amplified model vulnerability to several bias-inducing prompts, while reasoning reduced susceptibility of Qwen3-32B to one of the seven biases. The debiasing and few-shot prompting approaches demonstrated statistically significant reductions in biased responses across all three model architectures.

*Conclusion:*  
In none of the three LLMs, reasoning was able to consistently reduce vulnerability to bias-inducing prompts, revealing the fragility of the reasoning capabilities purported by the model developers.

## Models and data used in our study
As LLMs, we employ both Llama-3.3-70B with and without reasoning (R1 distillation) hosted on [together.ai](https://together.ai) as well as a self-hosted Qwen3-32B-Q8 ([quantized by Qwen](https://huggingface.co/Qwen/Qwen3-32B-GGUF)). Please see our code (section below) for the exact implementation.

We used the [BiasMedQA data](https://www.nature.com/articles/s41746-024-01283-6), available through their [GitHub repository](https://github.com/carlwharris/cog-bias-med-LLMs).

## Files contained in this repo
- *example_data_recency_bias.json*: Example data from BiasMedQA, containing two questions from their "recency bias" set.
- *bias_eval_r1.py*: Script to parse the two examples using together.ai's free API. Requires the `openai` package.
- *bias_eval_qwen3.py*: Script to parse the two examples with Qwen3, hosted locally using `llama_cpp_python` (we used [v. 0.3.8](https://pypi.org/project/llama-cpp-python/0.3.8/))
- *create_new_biases.py*: This script creates the four new biases (authority bias, premature closure, automation bias, simplicity bias) we introduced to uncover LLM memorization in Google Gemini 2.5 Flash.

## Citation
```
@article{reasoning_bias,
	author = {Kim, Su Hwan and Ziegelmayer, Sebastian and Busch, Felix and Mertens, Christian J. and Keicher, Matthias and Adams, Lisa C. and Bressem, Keno K. and Braren, Rickmer and Makowski, Marcus R. and Kirschke, Jan S. and Hedderich, Dennis M. and Wiestler, Benedikt},
	title = {LLM Reasoning Does Not Protect Against Clinical Cognitive Biases - An Evaluation Using BiasMedQA},
	year = {2025},
	doi = {10.1101/2025.06.22.25330078},
	URL = {https://www.medrxiv.org/content/10.1101/2025.06.22.25330078v1},
	journal = {medRxiv}
}
```
