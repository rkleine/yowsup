from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_contacts.protocolentities  import GetSyncIqProtocolEntity
import threading
import logging
logger = logging.getLogger(__name__)

class SyncLayer(YowInterfaceLayer):

    #This message is going to be replaced by the @param message in YowsupSendStack construction
    #i.e. list of (jid, message) tuples
    PROP_MESSAGES = "org.openwhatsapp.yowsup.prop.sendclient.queue"
    
    
    def __init__(self):
        super(SyncLayer, self).__init__()
        self.ackQueue = []
        self.lock = threading.Condition()

    #call back function when there is a successful connection to whatsapp server
    @ProtocolEntityCallback("success")
    def onSuccess(self, successProtocolEntity):
        self.lock.acquire()
        contacts= self.getProp(self.__class__.PROP_MESSAGES, [])
        contactEntity = GetSyncIqProtocolEntity(contacts)
        self.ackQueue.append(contactEntity.getId())
        self.toLower(contactEntity)
        self.lock.release()	

    #after receiving the message from the target number, target number will send a ack to sender(us)
    @ProtocolEntityCallback("iq")
    def onAck(self, entity):
        self.lock.acquire()
        #if the id match the id in ackQueue, then pop the id of the message out
        if entity.getId() in self.ackQueue:
            self.ackQueue.pop(self.ackQueue.index(entity.getId()))
            
        if not len(self.ackQueue):
            self.lock.release()
            logger.info("contacts sync")
            raise KeyboardInterrupt()

        self.lock.release()
