import tensorflow as tf
import numpy as np
import os
import time

from encoding import EncodedMidi, Tick
from generator import save

# set up tf environment
tf.enable_eager_execution()

class RNN:
    def __init__(self, midi_path):
        # make encoded midi
        self.midi = EncodedMidi(midi_path)
        self.ticks = self.midi.encoding

        # nique ticks
        vocab = []
        for tick in self.ticks:
            if tick not in vocab:
                vocab.append(tick)

        # Creating a pamming from nuique ticks to indices
        self.tick2idx = {u:i for i, u in enumerate(vocab)}
        self.idx2tick = np.array(vocab)
        
        self.ticks_as_int = np.array([self.tick2idx[t] for t in self.ticks])

        # The maximum length sentence we want for a single input in characters
        self.seq_length = 100
        self.examples_per_epoch = len(self.ticks)//self.seq_length

        # Create training examples / targets
        self.tick_dataset = tf.data.Dataset.from_tensor_slices(self.ticks_as_int)

        self.sequences = self.tick_dataset.batch(self.seq_length+1, drop_remainder=True)
        
        self.dataset = self.sequences.map(self.split_input_target)

        # Batch size 
        self.BATCH_SIZE = 64
        self.steps_per_epoch = self.examples_per_epoch//self.BATCH_SIZE

        # Buffer size to shuffle the dataset
        # (TF data is designed to work with possibly infinite sequences, 
        # so it doesn't attempt to shuffle the entire sequence in memory. Instead, 
        # it maintains a buffer in which it shuffles elements).
        self.BUFFER_SIZE = 10000

        self.dataset = self.dataset.shuffle(self.BUFFER_SIZE).batch(self.BATCH_SIZE, drop_remainder=True)

        # Length of the vocabulary in chars
        self.vocab_size = len(vocab)

        # The embedding dimension 
        self.embedding_dim = 256

        # Number of RNN units
        self.rnn_units = 1024

        if tf.test.is_gpu_available():
            self.rnn = tf.keras.layers.CuDNNGRU
        else:
            import functools
            self.rnn = functools.partial(
            tf.keras.layers.GRU, recurrent_activation='sigmoid')
        
        self.model = self.build_model(batch_size=self.BATCH_SIZE)

        # Compile the model
        self.model.compile(
            optimizer = tf.train.AdamOptimizer(),
            loss = tf.losses.sparse_softmax_cross_entropy)

        # Configure Checkpoints
        # Directory where the checkpoints will be saved
        self.checkpoint_dir = './training_checkpoints'
        # Name of the checkpoint files
        self.checkpoint_prefix = os.path.join(self.checkpoint_dir, "ckpt_{epoch}")

        self.checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
            filepath=self.checkpoint_prefix,
            save_weights_only=True)


    def train(self, epochs=20):
        self.history = self.model.fit(self.dataset.repeat(), epochs=epochs, steps_per_epoch=self.steps_per_epoch, callbacks=[self.checkpoint_callback])

    def generate_ticks(self, start_ticks, num_generate=1000):
        self.model = self.build_model(batch_size=1)
        self.model.load_weights(tf.train.latest_checkpoint(self.checkpoint_dir))

        self.model.build(tf.TensorShape([1, None]))
        # Evaluation step (generating text using the learned model)

        # Converting our start string to numbers (vectorizing) 
        input_eval = [self.tick2idx[t] for t in start_ticks]
        input_eval = tf.expand_dims(input_eval, 0)

        # Empty list to store our results
        ticks_generated = []

        # Low temperatures results in more predictable music.
        # Higher temperatures results in more surprising music.
        # Experiment to find the best setting.
        temperature = 1.0

        # Here batch size == 1
        self.model.reset_states()
        for i in range(num_generate):
            predictions = self.model(input_eval)
            # remove the batch dimension
            predictions = tf.squeeze(predictions, 0)

            # using a multinomial distribution to predict the word returned by the model
            predictions = predictions / temperature
            predicted_id = tf.multinomial(predictions, num_samples=1)[-1,0].numpy()
            
            # We pass the predicted word as the next input to the model
            # along with the previous hidden state
            input_eval = tf.expand_dims([predicted_id], 0)
            
            ticks_generated.append(self.idx2tick[predicted_id])

        return ticks_generated
    
    def build_model(self, batch_size):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Embedding(self.vocab_size, self.embedding_dim, 
                                    batch_input_shape=[batch_size, None]),
        self.rnn(self.rnn_units,
            return_sequences=True, 
            recurrent_initializer='glorot_uniform',
            stateful=True),
        tf.keras.layers.Dense(self.vocab_size)
        ])
        return self.model
    
    def split_input_target(self, chunk):
        input_text = chunk[:-1]
        target_text = chunk[1:]
        return input_text, target_text
    
rnn = RNN('./01Minuetto1.mid')
rnn.train(50)
#song = rnn.generate_ticks(start_ticks=rnn.ticks[0:5], num_generate=10000)
#save(song, rnn.midi.ticks_per_beat, "./ai2.mid")