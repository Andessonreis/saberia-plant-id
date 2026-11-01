import sys, os, time, numpy as np, torch, open_clip
from onnxruntime.quantization import quantize_dynamic, QuantType
import onnxruntime as ort
S, model_id = sys.argv[1], sys.argv[2]
tag = model_id.split("/")[-1]
model, _, pre = open_clip.create_model_and_transforms(f"hf-hub:{model_id}")
model.eval()
print(pre)
class Img(torch.nn.Module):
    def __init__(s, v): super().__init__(); s.v = v
    def forward(s, x): return torch.nn.functional.normalize(s.v(x), dim=-1)
m = Img(model.visual)
x = torch.randn(1, 3, 224, 224)
out = f"{S}/models/{tag}_visual_fp32.onnx"
torch.onnx.export(m, x, out, input_names=["pixel_values"], output_names=["embedding"], opset_version=17, dynamo=False)
q = f"{S}/models/{tag}_visual_int8.onnx"
quantize_dynamic(out, q, weight_type=QuantType.QInt8, per_channel=False, op_types_to_quantize=["MatMul"])
with torch.no_grad(): ref = m(x).numpy()
for f in (out, q):
    so = ort.SessionOptions(); so.intra_op_num_threads = 4
    s = ort.InferenceSession(f, so, providers=["CPUExecutionProvider"])
    s.run(None, {"pixel_values": x.numpy()})
    t0 = time.time()
    for _ in range(5): y = s.run(None, {"pixel_values": x.numpy()})[0]
    print(os.path.basename(f), f"{os.path.getsize(f)/1e6:.0f} MB", f"{(time.time()-t0)/5*1000:.0f} ms (4 threads PC)", "cos vs torch", float((y*ref).sum()))
