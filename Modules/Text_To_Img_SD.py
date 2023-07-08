"""
For Text_To_Img Diffusion
"""
from matplotlib import pyplot as plt
import torch
from diffusers import StableDiffusionPipeline, DDIMScheduler
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def build_SD_pipeline(checkpoint_path: str, device: str = 'cuda', **kwargs):
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
        pipe.scheduler = DDIMScheduler(beta_start=0.00085, beta_end=0.012,
                                       beta_schedule="scaled_linear", steps_offset=1, clip_sample=False)

    return pipe


def create_latents_from_seeds(pipeline, seeds, height, width, device):
    """
    Build latents from seeds for reusing seeds
    :param pipeline: Pipeline for model
    :param seeds: seed
    :param height: output Image Height
    :param width: output Image Width
    :param device: Torch device
    :return: seed controlled latent
    """
    generator = torch.Generator(device=device)
    latents = None
    # Get a new random seed, store it and use it as the generator state
    #seed = generator.seed()
    #seeds.append(seed)
    generator = generator.manual_seed(seeds)

    image_latents = torch.randn(
        (1, pipeline.unet.in_channels, height // 8, width // 8),
        generator=generator,
        device=device
    )
    latents = image_latents if latents is None else torch.cat((latents, image_latents))

    return latents


def make_img_prediction(pipeline, prompt: str, negative_prompt: str, **kwargs):
    """
    :param pipeline: The Diffusion pipeline used to generate Images
    :param prompt: The text prompt
    :param negative_prompt: The negative text prompt. i,e What you don't want
    :param kwargs: relevant arguments for the pipeline
    :return: Generated Images
    """
    latents = None
    if kwargs.get('device'):
        device = kwargs['device']
    else:
        device = 'cpu'


    # Manual Embedding of prompt. This is to counter the 77 Token limit imposed by CLIP
    max_length = pipeline.tokenizer.model_max_length

    input_ids = pipeline.tokenizer(prompt, truncation=False, padding="max_length",
                                   return_tensors="pt").input_ids
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

    # If generating from Seeds
    if kwargs['seeds']:
        latents = create_latents_from_seeds(pipeline=pipeline,
                                            seeds=kwargs['seeds'],
                                            height=kwargs['height'],
                                            width=kwargs['width'],
                                            device=kwargs['device'])
        latents = latents.type(torch.float16)

        image = pipeline(prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
                         guidance_scale=kwargs['CFG'], latents=latents).images[0]
    else:
        image = pipeline(prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
                         guidance_scale=kwargs['CFG']).images[0]

    return image
