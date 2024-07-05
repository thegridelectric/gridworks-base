

SDK for `gridworks-protocol <https://pypi.org/project/gridworks-protocol/>`_  Types
===========================================================================

The Python classes enumerated below provide an interpretation of gridworks-protocol
type instances (serialized JSON) as Python objects. Types are the building
blocks for all GridWorks APIs. You can read more about how they work
`here <https://gridworks.readthedocs.io/en/latest/api-sdk-abi.html>`_, and
examine their API specifications `here <apis/types.html>`_.
The Python classes below also come with methods for translating back and
forth between type instances and Python objects.


.. automodule:: gwbase.types

.. toctree::
   :maxdepth: 1
   :caption: TYPE SDKS

    BaseGNodeGt  <types/base-g-node-gt>
    GNodeGt  <types/g-node-gt>
    GNodeInstanceGt  <types/g-node-instance-gt>
    HeartbeatA  <types/heartbeat-a>
    Ready  <types/ready>
    SimTimestep  <types/sim-timestep>
    SuperStarter  <types/super-starter>
    SupervisorContainerGt  <types/supervisor-container-gt>
