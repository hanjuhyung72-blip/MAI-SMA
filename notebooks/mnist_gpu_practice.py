# %%
STUDENT_NAME = "본인 이름으로 변경"

import os, sys, json, time, uuid, subprocess, platform
from pathlib import Path
from datetime import datetime, timezone, timedelta
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

SEED = 42
tf.keras.utils.set_random_seed(SEED)
RUN_ID = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
OUTPUT_DIR = Path("/content/mnist_gpu_results") / RUN_ID
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

gpus = tf.config.list_physical_devices("GPU")
assert gpus, "GPU가 없습니다. 런타임 → 런타임 유형 변경 → GPU 선택 후 첫 셀부터 다시 실행하세요."
for gpu in gpus:
    try:
        tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError:
        pass

gpu_info = subprocess.check_output(
    ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
    text=True,
).strip()
with tf.device("/GPU:0"):
    gpu_check = tf.matmul(tf.ones((256, 256)), tf.ones((256, 256)))
    gpu_sum = float(tf.reduce_sum(gpu_check).numpy())
assert "GPU" in gpu_check.device, "행렬 연산이 GPU에 배치되지 않았습니다."

def evidence_header(number, title):
    print("=" * 72)
    print(f"EVIDENCE {number}/5 | {title}")
    print(f"Student: {STUDENT_NAME} | Run: {RUN_ID}")
    print(f"GPU: {gpu_info}")
    print("=" * 72)

evidence_header(1, "COLAB GPU CONNECTION")
print("Python:", platform.python_version(), "| TensorFlow:", tf.__version__)
print("TensorFlow GPU devices:", gpus)
print("GPU matrix result device:", gpu_check.device)
print("GPU matrix checksum:", gpu_sum)
print("GPU connection and actual matrix computation: SUCCESS")
if STUDENT_NAME == "본인 이름으로 변경":
    print("주의: 첫 줄 STUDENT_NAME을 본인 이름으로 수정하고 다시 실행하세요.")


# %%
(x_train_all, y_train_all), (x_test_raw, y_test) = tf.keras.datasets.mnist.load_data()

x_train_all = x_train_all.astype("float32")[..., np.newaxis] / 255.0
x_test = x_test_raw.astype("float32")[..., np.newaxis] / 255.0
order = np.random.default_rng(SEED).permutation(len(x_train_all))
x_train = x_train_all[order[:54000]]
y_train = y_train_all[order[:54000]]
x_val = x_train_all[order[54000:]]
y_val = y_train_all[order[54000:]]

evidence_header(2, "MNIST DATA AND VISUALIZATION")
print(f"Train: {x_train.shape} | Validation: {x_val.shape} | Test: {x_test.shape}")
print(f"Pixel range: [{x_train.min():.1f}, {x_train.max():.1f}] | Classes: 0-9")
fig, axes = plt.subplots(3, 6, figsize=(11, 4.8))
for i, ax in enumerate(axes.flat):
    ax.imshow(x_train[i, :, :, 0], cmap="gray")
    ax.set_title(f"Label: {y_train[i]}", fontsize=10)
    ax.axis("off")
fig.suptitle(f"MNIST Training Samples | Run {RUN_ID}", fontsize=13)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "02_mnist_samples.png", dpi=160, bbox_inches="tight")
plt.show()


# %%
EPOCHS = 3
BATCH_SIZE = 128
tf.keras.backend.clear_session()
tf.keras.utils.set_random_seed(SEED)

with tf.device("/GPU:0"):
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(28, 28, 1)),
        tf.keras.layers.Conv2D(32, (3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(10, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    evidence_header(3, "CNN TRAINING ON GPU")
    print("Architecture: Conv2D(32) -> Pool -> Conv2D(64) -> Pool -> Dense(64) -> Dropout -> Dense(10)")
    print(f"Parameters: {model.count_params():,} | Epochs: {EPOCHS} | Batch size: {BATCH_SIZE}")
    print("Requested training device: /GPU:0")
    print("First weight device:", getattr(getattr(model.trainable_variables[0], "handle", None), "device", "See GPU tensor check in evidence 1"))
    start = time.perf_counter()
    history = model.fit(x_train, y_train, validation_data=(x_val, y_val),
                        epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=2)
    training_seconds = time.perf_counter() - start

print(f"Training completed in {training_seconds:.2f} seconds")
print(f"Final training accuracy: {history.history['accuracy'][-1]:.4%}")
print(f"Final validation accuracy: {history.history['val_accuracy'][-1]:.4%}")


# %%
test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)
evidence_header(4, "TEST METRICS AND LEARNING CURVES")
print(f"Test samples: {len(y_test):,} | Test accuracy: {test_accuracy:.4%} | Test loss: {test_loss:.6f}")
epochs_axis = np.arange(1, EPOCHS + 1)
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(epochs_axis, history.history["accuracy"], "o-", label="Train")
axes[0].plot(epochs_axis, history.history["val_accuracy"], "o-", label="Validation")
axes[0].set(title="Accuracy", xlabel="Epoch", ylabel="Accuracy", xticks=epochs_axis)
axes[1].plot(epochs_axis, history.history["loss"], "o-", label="Train")
axes[1].plot(epochs_axis, history.history["val_loss"], "o-", label="Validation")
axes[1].set(title="Loss", xlabel="Epoch", ylabel="Cross-entropy", xticks=epochs_axis)
for ax in axes:
    ax.legend()
    ax.grid(alpha=0.25)
fig.suptitle(f"CNN Learning Curves | Test accuracy {test_accuracy:.2%} | Run {RUN_ID}", fontsize=11)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "04_learning_curves.png", dpi=160, bbox_inches="tight")
plt.show()


# %%
probabilities = model.predict(x_test, batch_size=256, verbose=0)
predicted = np.argmax(probabilities, axis=1)
cm = np.zeros((10, 10), dtype=np.int64)
np.add.at(cm, (y_test, predicted), 1)
correct = np.flatnonzero(predicted == y_test)
wrong = np.flatnonzero(predicted != y_test)
selected = list(correct[:3]) + list(wrong[:3])
if len(selected) < 6:
    selected += [int(i) for i in correct if i not in selected][:6-len(selected)]

evidence_header(5, "CONFUSION MATRIX AND PREDICTIONS")
print(f"Correct: {len(correct):,} | Incorrect: {len(wrong):,} | Accuracy: {len(correct)/len(y_test):.4%}")
fig = plt.figure(figsize=(12, 5.2), layout="constrained")
grid = fig.add_gridspec(2, 5, width_ratios=[1.3, 1.3, 1, 1, 1])
ax_cm = fig.add_subplot(grid[:, :2])
ax_cm.imshow(cm, cmap="Blues")
ax_cm.set(xticks=range(10), yticks=range(10), xlabel="Predicted digit", ylabel="True digit", title="Confusion Matrix")
threshold = cm.max() * 0.5
for r in range(10):
    for c in range(10):
        ax_cm.text(c, r, str(cm[r, c]), ha="center", va="center", fontsize=7,
                   color="white" if cm[r, c] > threshold else "black")
for n, i in enumerate(selected):
    ax = fig.add_subplot(grid[n//3, 2+n%3])
    ax.imshow(x_test_raw[i], cmap="gray")
    ax.set_title(f"True {y_test[i]} / Pred {predicted[i]}\nConfidence {probabilities[i, predicted[i]]:.1%}",
                 fontsize=9, color="seagreen" if y_test[i] == predicted[i] else "firebrick")
    ax.axis("off")
fig.suptitle(f"CNN Test Predictions | Run {RUN_ID}", fontsize=12)
fig.savefig(OUTPUT_DIR / "05_confusion_and_predictions.png", dpi=160, bbox_inches="tight")
plt.show()


# %%
DOWNLOAD_RESULTS = False
import csv, shutil
metrics = {
    "student": STUDENT_NAME, "run_id": RUN_ID, "gpu": gpu_info,
    "tensorflow_version": tf.__version__, "gpu_check_device": gpu_check.device,
    "seed": SEED, "epochs": EPOCHS, "batch_size": BATCH_SIZE,
    "training_samples": len(y_train), "validation_samples": len(y_val), "test_samples": len(y_test),
    "training_seconds": training_seconds, "test_accuracy": float(test_accuracy), "test_loss": float(test_loss),
    "incorrect_test_predictions": int(len(wrong)),
}
(OUTPUT_DIR / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
with (OUTPUT_DIR / "training_history.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["epoch", "accuracy", "val_accuracy", "loss", "val_loss"])
    for i in range(EPOCHS):
        writer.writerow([i+1] + [history.history[k][i] for k in ["accuracy", "val_accuracy", "loss", "val_loss"]])
model.save(OUTPUT_DIR / "mnist_cnn.keras")
archive = shutil.make_archive(str(OUTPUT_DIR), "zip", OUTPUT_DIR)
print("Actual execution results saved:", archive)
if DOWNLOAD_RESULTS:
    from google.colab import files
    files.download(archive)
