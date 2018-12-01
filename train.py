import tensorflow as tf
import numpy as np
import os
import time

from encoding import EncodedMidi, Tick
from generator import save

# set up tf environment
tf.enable_eager_execution()

"""DATA INPUT"""
# make encoded midi
midi = EncodedMidi('./01Minuetto1.mid')
ticks = midi.encoding

# unique ticks
vocab = []
for tick in ticks:
    if tick not in vocab:
        vocab.append(tick)

# vectorize "text"
# Creating a mapping from unique ticks to indices
tick2idx = {u:i for i, u in enumerate(vocab)}
idx2tick = np.array(vocab)
ticks_as_int = np.array([tick2idx[t] for t in ticks])

# The maximum length sentence we want for a single input in characters
seq_length = 100
examples_per_epoch = len(ticks)//seq_length

# Create training examples / targets
tick_dataset = tf.data.Dataset.from_tensor_slices(ticks_as_int)

sequences = tick_dataset.batch(seq_length+1, drop_remainder=True)

def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text

dataset = sequences.map(split_input_target)

# Batch size 
BATCH_SIZE = 64
steps_per_epoch = examples_per_epoch//BATCH_SIZE

# Buffer size to shuffle the dataset
# (TF data is designed to work with possibly infinite sequences, 
# so it doesn't attempt to shuffle the entire sequence in memory. Instead, 
# it maintains a buffer in which it shuffles elements).
BUFFER_SIZE = 10000

dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)


"""TRAINING"""
# Length of the vocabulary in chars
vocab_size = len(vocab)

# The embedding dimension 
embedding_dim = 256

# Number of RNN units
rnn_units = 1024

if tf.test.is_gpu_available():
  rnn = tf.keras.layers.CuDNNGRU
else:
  import functools
  rnn = functools.partial(
    tf.keras.layers.GRU, recurrent_activation='sigmoid')

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(vocab_size, embedding_dim, 
                                  batch_input_shape=[batch_size, None]),
    rnn(rnn_units,
        return_sequences=True, 
        recurrent_initializer='glorot_uniform',
        stateful=True),
    tf.keras.layers.Dense(vocab_size)
    ])
    return model

model = build_model(
    vocab_size = len(vocab), 
    embedding_dim=embedding_dim, 
    rnn_units=rnn_units, 
    batch_size=BATCH_SIZE)

for input_example_batch, target_example_batch in dataset.take(1): 
  example_batch_predictions = model(input_example_batch)
  print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")

sampled_indices = tf.multinomial(example_batch_predictions[0], num_samples=1)
sampled_indices = tf.squeeze(sampled_indices,axis=-1).numpy()

# Compile the model
model.compile(
    optimizer = tf.train.AdamOptimizer(),
    loss = tf.losses.sparse_softmax_cross_entropy)

# Configure Checkpoints
# Directory where the checkpoints will be saved
checkpoint_dir = './training_checkpoints'
# Name of the checkpoint files
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True)


"""Train the model"""
EPOCHS = 3

history = model.fit(dataset.repeat(), epochs=EPOCHS, steps_per_epoch=steps_per_epoch, callbacks=[checkpoint_callback])

model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)

model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))

model.build(tf.TensorShape([1, None]))

def generate_ticks(model, start_ticks):
  # Evaluation step (generating text using the learned model)

  # Number of ticks to generate
  num_generate = 1000

  # Converting our start string to numbers (vectorizing) 
  input_eval = [tick2idx[t] for t in start_ticks]
  input_eval = tf.expand_dims(input_eval, 0)

  # Empty list to store our results
  ticks_generated = []

  # Low temperatures results in more predictable music.
  # Higher temperatures results in more surprising music.
  # Experiment to find the best setting.
  temperature = 1.0

  # Here batch size == 1
  model.reset_states()
  for i in range(num_generate):
      predictions = model(input_eval)
      # remove the batch dimension
      predictions = tf.squeeze(predictions, 0)

      # using a multinomial distribution to predict the word returned by the model
      predictions = predictions / temperature
      predicted_id = tf.multinomial(predictions, num_samples=1)[-1,0].numpy()
      
      # We pass the predicted word as the next input to the model
      # along with the previous hidden state
      input_eval = tf.expand_dims([predicted_id], 0)
      
      ticks_generated.append(idx2tick[predicted_id])

  return ticks_generated

song = generate_ticks(model, start_ticks=ticks[0:5])
save(song, './ai.mid')