
def actionWarBase():

	messages = getMessages();

	for message in messages:
		if(message.getMessage() == "whereAreYouBase"):
			setDebugString("I'm here base PY");
			sendMessage(message.getSenderID(), "here", "");

	return idle();
