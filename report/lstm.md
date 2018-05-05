# LSTM RNNs (Long Short-Term Memory Recurrent Neural Nets)

### Overview
The other approach we used to generate lyrics was through a RNN, but specifically an **LSTM** RNN. The primary difference in the LSTM is its inherent ability to learn long-term dependencies in the data, whereas a regular RNN is severely limited in this regard.

This prominent difference is due to the increased complexity of the network's update equation:

![Regular RNN](./regular_rnn.png)

As seen above, a regular RNN simply contains repeating, single **tanh** layers.

![LSTM RNN](./lstm_rnn.png)

On the other hand, LSTM layers contain four, interacting neural network layers of point-wise operations (i.e. vector addition), concatenation, and copying of vectors to different locations within each network cell.

### Character-Level vs. Word-Level Models
We trained two types of LSTM RNNs: one models the data at a *character* level, predicting the subsequent **character** given a pre-specified input sequence; the other models the data at a *word* level, predicting the subsequent **word** given a pre-specified input sequence. This prediction is repeatedly performed until the specified character or word length threshold is reached.

### Training

#### Softmax Classifier (Cross-Entropy Loss)
We run the same training process for both the character-level and word-level RNN: given an input sequence (i.e. "The sky is"), we one-hot encode each character (or word) into individual vectors, then feed each into the RNN iteratively. This ultimately produces a sequence of **n**-dimensional output vectors (one for each character or word in the input sequence), containing confidence scores the RNN assigns for the subsequent character or word in the sequence:

![Training Process](./training.jpeg)

This confidence score assignment is repeated continuously until the scores converge, determined through the LSTM's backpropagation algorithm which determines what directions the LSTM should adjust the network weights to. Ultimately, this increases the confidence of the "expected" subsequent character or word. In our project's case, we use **mini-batch gradient descent** to accomplish this goal. Compared to stochastic gradient descent and batch gradient descent, mini-batch succeeds in its ability to more quickly converge the confidence scores, while its increased frequency in updating the model's states allows computational efficiency due to not having all training data in memory. This helped tremendously in improving our model's predictive capabilities, especially due to our time constraints (Tuesday team rip).

#### Perplexity Scoring
The metric we use to determine the "correctness" of our model's predictions is through the **perplexity** function, shown below:

<center>
![Perplexity](./perplexity.png)
</center>

where ***p<sub>target<sub>i</sub></sub>*** is the probability of character or word ***i*** occurring as the prediction. The character-level RNN converged to a lower perplexity score in comparison to the word-level RNN, shown below:

<center>
![Training Loss - Perplexity](./training_perplexity.png)
</center>

### Results

#### Word-Level Model
> Canada, coming Griffith baritone, friend's<br>
> Gotta roll a Wraith n\*\*\*\*\* to aim for soon on y'all back after now<br>
> Now you're Toaster, and overlook my Girls from Care<br>
> I'm a good girl too got you had the dead<br>
> Mothaf\*\*\*a feel let 'em knew good some same girls, ever make it like

As seen above, the word-level model doesn't capture grammatical syntax very well. We concluded it is primarily due to the size of our training data, as Drake only has ~140 songs released by himself + singles.

#### Character-Level Model

###### Epoch 1
> Why it wacting you frop tels and bezy so<br>
> That’s you prised<br>
> Intuigh ofrest<br>
> And o lith be’ve the lasle

###### Epoch 25
> Yeah dink ya is laying all you hands<br>
> Why I’m in the virtion that right?<br>
> When she could ever put the costs with me<br>
> I’m the one she can so getting in my knees<br>
> When I be right around my hands for my own peace”

###### Epoch 50
> And I’m feeling so low with a good go<br>
> That’s why I ain’t all that I made<br>
> I just need a way, on and on I about to lose everyday

For the character-level model, the RNN progressively begins to understand grammatical syntax, and at epoch **50**, it begins to model internal rhyming. We concluded that the character-level RNN ended up performing significantly better after a long period of training due to the smaller size of our training corpus - with more data to train on, the word-level model would likely perform at a similar level as the character-level RNN.
