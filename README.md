osvalbot
========

Markov chain stuff stolen from twisted tutorial http://eflorenzano.com/blog/2008/11/17/writing-markov-chain-irc-bot-twisted-and-python/

Also has commands, can classify as positive or negative using a naive bayes classifier trained or some twitter data. Can increment karma for people, and view said karma.

Need to do !train before classifying works.

Karma
------
    <ben> osvalbot: !inc *name*
    <osvalbot> (incremented *name*)
    <ben> osvalbot: !karma *name*
    <osvalbot> (= 1 (karma *name*))
