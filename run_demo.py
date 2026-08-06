from pipeline.pipeline import DataPipeline

print("========== V5 TRAINING DATA EXECUTION ==========")

pipeline = DataPipeline()

pipeline.run()

print("Phase 1 completed.")

from src.mixture_scheduler import *
from src.packing import *
from src.masks import *

scheduler = MixtureScheduler()

scheduler.add_stage(
    MixtureStage(
        name="pretraining",
        lane_weights={
            "general":0.50,
            "code":0.20,
            "indic":0.10,
            "reasoning":0.20
        },
        protected_floors={
            "indic":0.08,
            "reasoning":0.05
        }
    )
)

print("Mixture Stage:", scheduler.get_stage(0).name)

packer = PackingEngine()

sample = list(range(1,65))

packed = packer.pack(sample,32)

print("Packed sequences:", len(packed))

loss = create_loss_mask(packed[0])

attention = create_attention_mask(packed[0])

positions = create_position_ids(packed[0])

print("Loss mask length:", len(loss))
print("Attention mask length:", len(attention))
print("Position IDs:", len(positions))
