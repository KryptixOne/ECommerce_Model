# StyleNexus

<img src="https://github.com/KryptixOne/ECommerce_Model/blob/main/webApp_Flask/static/Video_Gif.gif" alt="StylNexus Demo">




<details>
  <summary>Setup</summary>
  Setup is work in progress. Goal is to use the Dockerfile with the cuda base image. Currently requirements contain torch although base image provides them too.
  Structure of checkpoints:

  ```
  checkpoints/
├── Lora
├── Photon_inpaint
└── SAM_Checkpoint
  ```

</details>

---

### Inference Usage:
1. For local usage for inference, open `main.py`
2. set the followiwng parameters in `def main()`
```
seeds = None 
scheduler = "DDIM"
reference_image_path = Set to input image path
checkpoint_directory_SD = set to checkpoint directory for Diffusion model
checkpoint_path_SAM = set to checkpoint directory for SAM model
direct = set to directory for output image
lora_path = set to lora file path. None if no lora
lora_alpha = Value between [0-1] Sets lora integration. 0: no lora. 1: full lora
device = "cuda"
prompt = "(A sexy model with sunglasses wearing a T-Shirt), simple plain background"
negative_prompt = ('cartoon, painting, illustration, (worst quality, low quality, normal quality:2), NSFW'
   )
segmentation_prompt = 'a photo of a T-shirt' 
num_inference_steps_list = [50]  # The number of denoising steps. Higher number usually leads to higher quality
cfg_list = [6] #6 is awesome
height = 784 # desired output image height
width = 512 # desired output image width
border_mask_width = 8 # how large border fix should be
img2img_strength_first_pass = [0.9] # 0.9 on first. Heavy alteration should be given
img2img_strength_second_pass = [0.5] #0.4 -0.5 best visual # lower to reduce effects of superimposition but also to limit border distortion
HyperParameterTune_num = 1
```
3. checkpoints available: [Google Drive](https://drive.google.com/drive/folders/15aWgJfne3cZ5Im7w3N_-XX3MMmg-gLno?usp=sharing)
4. run `main.py` after values have been set.
---

### Hyperparameter Usage:
1. set `HyperParameterTune_num` to a value `>1`
2. following hyperparameters are tune-able:
```
num_inference_steps_list = list of desirable values
cfg_list = list of desirable values
img2img_strength_first_pass = list of desirable values
img2img_strength_second_pass = list of desirable values
```
---
### Flask Webapp Usage:
1. run `python ./webApp_Flask/webApp_flask.py` in terminal
2. click on the link that apperas in the terminal

---
    
<img src="https://github.com/KryptixOne/ECommerce_Model/blob/main/OutputPics_Issues/GirlWearingLion.PNG" alt="Original Photo" width="30%"> <img src="https://github.com/KryptixOne/ECommerce_Model/blob/main/OutputPics_Issues/outputnew.png" alt="Inpainted Photo" width="30%">

See left: Original Image, Right: Inpainted Image. Notice the alterations occurs during inpainting

#### Update on Issue:
Problem showing improvements after updating model weights.

Merging Inpainting Model V1.5 with Model not used for in-painting updates successfully according to the following:
A +(B-C) 
Where A is Inpaint Model, B is our Model, and C is the non-inpaint version of A

Note we also choose a merge multiplier of 1.

See results below

<img src="https://github.com/KryptixOne/ECommerce_Model/blob/main/OutputPics_Issues/ErroneousMale%20Model.png" alt="Original_superimposed Photo" width="30%"> <img src="https://github.com/KryptixOne/ECommerce_Model/blob/main/OutputPics_Issues/With_New_inpaintModel.png" alt="Inpainted_model Photo" width="30%">


