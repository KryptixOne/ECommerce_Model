"""
Project Should do the following:

1. Take the following as inputs from the User: [ ]
    a. sequence of Reference Images [ ]
    b. Desired Prompt [ ]
    c. Desired Negative Prompt. Or This can be predetermined by us. [ ]

2. Identify area of interest based on reference images. [ ]
    --> Create masks with segmentation net. [ ]
    --> Define Inpainting area [ ]
    --> Define Border of Inpainting area for Second pass to smooth border artifacts [ ]
    --> If using DreamBooth-like methodology, Not required

3. Incorporate Visual Similarity Metric.  [ ]
    --> Metric will rate how "similar" the generated object is to reference.  [ ]
    --> can use segmentation net to identify AoI [ ]
    --> Need to determine this metric still. As variation, pose, angle, lighting, etc. should not negatively affect
    the Metric but visual distortions to the reference should [ ]

4. Incorporate Image Filtering Based on Similarity Metric [ ]
    --> Remove Images that don't achieve a certain threshold. [ ]
    --> For Successful Images, Log Hyperparameters, seed, and reference Images (useful for future training) [ ]
    --> Return X number of Generated Images [ ]

5. Build a WebUI that Allows for independent user usage [ ]
"""
from matplotlib import pyplot as plt
from PIL import Image
import torch
from transformers import CLIPTextModel, CLIPTokenizer
from diffusers import AutoencoderKL, UNet2DConditionModel, PNDMScheduler

from tqdm.auto import tqdm
from diffusers import StableDiffusionPipeline, DDIMScheduler

def build_SD_pipeline(checkpoint_path:str, device:str = 'cuda' ,**kwargs):
    """
    :param checkpoint_path: Checkpoint path to Diffusers Type Folder Containing the VAE, UNET, Scheduler, text_encoder
    tokenizer
    :param device: string name of the device used for DL and inference. Default is 'cuda'
    :return: Pipeline for Stable Diffusion given a model
    """

    assert checkpoint_path, 'Checkpoint_path is empty'
    pipe = StableDiffusionPipeline.from_pretrained(checkpoint_path, torch_dtype=torch.float16)
    pipe = pipe.to(device)

    # Enables DDIM scheduler for Stable Diffusion Models
    if kwargs.get('scheduler') == 'DDIM':
        # This Scheduler may need to be tuned
        pipe.scheduler = DDIMScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear", steps_offset=1, clip_sample=False)

    return pipe

def make_img_prediction(pipeline, prompt:str, negative_prompt:str, *kwargs):
    """
    :param pipeline: The Diffusion pipeline used to generate Images
    :param prompt: The text prompt
    :param negative_prompt: The negative text prompt. i,e What you don't want
    :param kwargs: relevant arguments for the pipeline
    :return: Generated Images
    """
    if kwargs.get('device'):
        device = kwargs['device']
    else:
        device = 'cpu'

    # Manual Embedding of prompt. This is to counter the 77 Token limit imposed by CLIP
    max_length = pipeline.tokenizer.model_max_length

    input_ids = pipeline.tokenizer(prompt, return_tensors="pt").input_ids
    input_ids = input_ids.to(device)

    negative_ids = pipeline.tokenizer(negative_prompt, truncation=False, padding="max_length",
                                  max_length=input_ids.shape[-1], return_tensors="pt").input_ids

    negative_ids = negative_ids.to(device)

    concat_embeds = []
    neg_embeds = []
    for i in range(0, input_ids.shape[-1], max_length):
        concat_embeds.append(pipeline.text_encoder(input_ids[:, i: i + max_length])[0])
        neg_embeds.append(pipeline.text_encoder(negative_ids[:, i: i + max_length])[0])

    prompt_embeds = torch.cat(concat_embeds, dim=1)
    negative_prompt_embeds = torch.cat(neg_embeds, dim=1)

    image = pipeline(prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds).images[0]

    return image


