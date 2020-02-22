from ..models.dummy import Dummy
from ..system import PianoReductionSystem
from ..piano.pre_processor import StructuralPreProcessor
from ..piano import algorithm, alignment, contraction


system = PianoReductionSystem(
    name='dummy',
    pre_processor=StructuralPreProcessor(
        algorithms=[
            ],
        alignment=alignment.AlignMinOctaveMatching(use_hand=False),
        contractions=[
            contraction.ContractTies(),
            contraction.ContractByPitchOnset(),
            ],
        ),
    Model=Dummy,
    )


if __name__ == '__main__':
    system.run_cli()
