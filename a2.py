from typing import Dict, List, Optional
from a2_support import *


class PokemonStats:
    """A class modelling the stats of a pokemon. These stats must be
    non-negative.
    
    Examples:
        >>> stats = PokemonStats((1, 100, 110, 120))
        >>> stats.get_hit_chance()
        1
        >>> stats.get_max_health()
        100
        >>> stats.get_attack()
        110
        >>> stats.get_defense()
        120
        >>> str(stats)
        'PokemonStats((1, 100, 110, 120))'
        >>> repr(stats)
        'PokemonStats((1, 100, 110, 120))'
    """

    def __init__(self, stats: Stats) -> None:
        """Constructs an instance of PokemonStats.
        
        The format of the incoming stats are:
            `(hit_chance, health, attack, defense)` with the indices
            given by constants in the support code.
        
        Parameters:
            * `stats`: The base list of stats to encapsulate. *These values
            can be assumed to be non-negative*
        """
        self._stats = stats

    def level_up(self) -> None:
        """Grows the PokemonStats instance after the pokemon has levelled up.
        
        On leveling up, the base hit chance should always be = `1`, while the
        remaining stats grow by `5%` and are rounded down.

        Examples:
            >>> stats = PokemonStats((1, 100, 110, 120))
            >>> stats.level_up()
            >>> stats.get_hit_chance()
            1
            >>> stats.get_max_health()
            105
            >>> stats.get_attack()
            115
            >>> stats.get_defense()
            126
        """
        self._stats = [int(stat * LEVEL_UP_STAT_GROWTH) for stat in
                       self._stats]
        self._stats[STAT_HIT_CHANCE] = 1

    def get_hit_chance(self) -> float:
        """Return the pokemon's current chance at making a successful
        attack."""
        return self._stats[STAT_HIT_CHANCE]

    def get_max_health(self) -> int:
        """Return the pokemon's max health"""
        return self._stats[STAT_MAX_HEALTH]

    def get_attack(self) -> int:
        """Return the pokemon's attack stat"""
        return self._stats[STAT_ATTACK]

    def get_defense(self) -> int:
        """Return the pokemon's defense stat"""
        return self._stats[STAT_DEFENSE]

    def apply_modifier(self, modifier: Stats) -> 'PokemonStats':
        """Applies a stat modifier and returns the newly constructed, modified
        pokemon stats.
        
        The resulting pokemon stats are the elementwise sum of the current stats
        and incoming modification and should be bound by 0.

        Parameters:
            * `modifier`: A list of stat modifications to apply, of the same
                    structure as the initial supplied pokemon stats.

        Examples:
            >>> stats = PokemonStats((1, 100, 110, 120))
            >>> modified_stats = stats.apply_modifier((-0.5, -20, -10, -5))
            >>> stats.get_hit_chance()
            1
            >>> modified_stats.get_hit_chance()
            0.5
            >>> stats.get_max_health()
            100
            >>> modified_stats.get_max_health()
            80
        """
        result = []
        # Students are not expected to know the zip function and can use
        # something else, e.g. enumerate
        for stat, modification in zip(self._stats, modifier):
            result.append(max(0, stat + modification))
        return PokemonStats(tuple(result))  # type: ignore

    def __str__(self) -> str:
        """Returns the string representation of this class."""
        return f'PokemonStats({repr(self._stats)})'

    def __repr__(self) -> str:
        """Returns the string representation of this class."""
        return str(self)


class Pokemon:
    """ A class which represents a Pokemon.
    
    A pokemon's level is determined by its experience points, through
    the formula: `level = floor(experience ^ (1/3))`.

    A pokemon can learn a maximum of 4 moves.

    Examples:
        >>> stats = PokemonStats((1, 100, 200, 200))
        >>> pokemon = Pokemon("Pikachu", stats, 'electric', [], level=5)
        >>> pokemon.get_name()
        'Pikachu'
        >>> pokemon.get_health()
        100
        >>> pokemon.get_max_health()
        100
        >>> pokemon.get_element_type()
        'electric'
        >>> pokemon.get_level()
        5
        >>> pokemon.get_experience()
        125
        >>> pokemon.get_next_level_experience_requirement()
        216
        >>> pokemon.has_fainted()
        False
        >>> str(pokemon)
        'Pikachu (lv5)'

    For future examples in this class, you can assume the above example was
    run first.
    """

    def __init__(self, name: str, stats: PokemonStats, element_type: str,
                 moves: List['Move'], level: int = 1) -> None:
        """Creates a Pokemon instance.
        
        Parameters:
            * `name`: The name of this pokemon
            * `stats`: The pokemon's stats
            * `element_type`: The name of the type of this pokemon.
            * `moves`: A list of containing the moves that this pokemon will
                    have learned after it is instantiated.
            * `level`: The pokemon's level.
        """
        self._name = name
        self._element_type = element_type

        self._stats = stats
        # tuples of <modifications, rounds_remaining> applied during combat.
        # e.g. A pokemon might use a move which increases their attack for a
        # few turns.
        self._stat_modifiers: List[Tuple[Stats, int]] = []

        self._health = stats.get_max_health()

        self._level = level
        self._experience = level ** 3

        # A dictionary of moves to their remaining uses
        self._moves: Dict[Move, int] = {}
        for move in moves:
            if self.can_learn_move(move):
                self.learn_move(move)

    def get_name(self) -> str:
        """Get this pokemon's name."""
        return self._name

    def get_health(self) -> int:
        """Get the remaining health of this pokemon."""
        return self._health

    def get_max_health(self) -> int:
        """Get the maximum health of this pokemon before stat modifiers
        are applied."""
        return self._stats.get_max_health()

    def get_element_type(self) -> str:
        """Get the name of the type of this pokemon."""
        return self._element_type

    def get_remaining_move_uses(self, move: 'Move') -> int:
        """Gets the number of moves left for the supplied move, or
        0 if the pokemon doesn't know the move."""
        return self._moves.get(move, 0)

    def get_level(self) -> int:
        """Get the level of this pokemon."""
        return self._level

    def get_experience(self) -> int:
        """Return the current pokemon's experience."""
        return self._experience

    def get_next_level_experience_requirement(self) -> int:
        """Return the total experience required for the pokemon to be one level
        higher.
        """
        return (self._level + 1) ** 3

    def get_move_info(self) -> List[Tuple['Move', int]]:
        """Return a list of the pokemon's known moves and their remaining uses.

        This list should be sorted by the name of the moves.
        
        Examples:
            >>> tackle = Attack('tackle', 'normal', 15, 80, 50, .95)
            >>> flamethrower = Attack('flamethrower', 'fire', 10, 80, 60, 0.8)
            >>> pokemon.get_move_info()
            []
            >>> pokemon.learn_move(tackle)
            >>> pokemon.learn_move(flamethrower)
            >>> pokemon.get_move_info()
            [(Attack('flamethrower', 'fire', 10), 10), (Attack('tackle', 'normal', 15), 15)]
        """
        return sorted(self._moves.items(),
                      key=lambda move_info: move_info[0].get_name())

    def has_fainted(self) -> bool:
        """Return true iff the pokemon has fainted."""
        return self._health == 0

    def modify_health(self, change: int) -> None:
        """Modify the pokemons health by the supplied amount. 
        
        The resulting health is clamped between 0 and the max health
        of this pokemon after stat modifiers are applied.

        Parameters:
            * `change`: The health change to be applied to the pokemon.

        Examples:
            >>> pokemon.get_max_health()
            100
            >>> pokemon.get_health()
            100
            >>> pokemon.modify_health(-20)
            >>> pokemon.get_health()
            80
            >>> pokemon.modify_health(30)
            >>> pokemon.get_health()
            100
            >>> pokemon.modify_health(-9000)
            >>> pokemon.get_health()
            0
            >>> pokemon.has_fainted()
            True
        """
        max_health = self.get_stats().get_max_health()
        self._health = max(0, min(self._health + change, max_health))

    def gain_experience(self, experience: int) -> None:
        """ Increase the experience of this pokemon by the supplied amount, and
        level up if necessary.

        Parameters:
            * `experience`: The amount of experience points to increase.
        """
        self._experience += experience
        start_level = self._level
        end_level = int(self._experience ** (1.0 / 3))

        for _ in range(end_level - start_level):
            self.level_up()

    def level_up(self) -> None:
        """Increase the level of this pokemon.
        
        leveling up grows the pokemon's stats, and increase its current health
        by the amount that the maximum hp increased.

        Examples:
            >>> pokemon.get_health()
            100
            >>> pokemon.get_max_health()
            100
            >>> pokemon.modify_health(-20)
            >>> pokemon.get_health()
            80
            >>> pokemon.level_up()
            >>> pokemon.get_health()
            85
            >>> pokemon.get_max_health()
            105
        """
        self._level += 1
        old_max_hp = self.get_max_health()
        self._stats.level_up()
        self.modify_health(self.get_max_health() - old_max_hp)

    def experience_on_death(self) -> int:
        """The experience awarded to the victorious pokemon if this pokemon
        faints.
        
        This is calculated through the formula:
            `200 * level / 7` and rounded down to the nearest integer,
            where `level`: the level of the pokemon who fainted.
        """
        return int(200 * self._level / 7)

    def can_learn_move(self, move: 'Move') -> bool:
        """Returns true iff the pokemon can learn the given move. i.e. they
        have learned less than the maximum number of moves for a pokemon and
        they haven't already learned the supplied move.
        """
        if len(self._moves) >= MAXIMUM_MOVE_SLOTS:
            return False

        # Can't learn the move if we've already learnt it
        return move not in self._moves

    def learn_move(self, move: 'Move') -> None:
        """
        Learns the given move, assuming the pokemon is able to.

        After learning this move, this Pokemon can use this move for `max_uses`
        times. See `Move.__init__`.

        Parameters:
            * `move`: move for pokemon to learn

        """
        self._moves[move] = move.get_max_uses()

    def forget_move(self, move: 'Move') -> None:
        """Forgets the supplied move, if the pokemon knows it."""
        if move in self._moves:
            self._moves.pop(move)

    def has_moves_left(self) -> bool:
        """Returns true iff the pokemon has any moves they can use"""
        for move in self._moves:
            if self._moves[move] > 0:
                return True
        return False

    def reduce_move_count(self, move: 'Move') -> None:
        """Reduce the move count of the move if the pokemon has learnt it."""
        if move in self._moves:
            uses = self._moves[move]
            self._moves[move] = max(0, uses - 1)

    def add_stat_modifier(self, modifier: Stats, rounds: int) -> None:
        """Adds a stat modifier for a supplied number of rounds.
        
        Parameters:
            * `modifier`: A stat modifier to be applied to the pokemon.
            * `rounds`: The number of rounds that the stat modifier will be in
                    effect for.
        """
        self._stat_modifiers.append((modifier, rounds))
        self.modify_health(0)

    def get_stats(self) -> PokemonStats:
        """Return the pokemon stats after applying all current modifications."""
        result = self._stats
        for stat_modifier, _ in self._stat_modifiers:
            result = result.apply_modifier(stat_modifier)
        return result

    def post_round_actions(self) -> None:
        """Update the stat modifiers by decrementing the remaining number of
        rounds they are in effect for.
        
        Hint: students should make sure that the pokemon's health is updated
        appropriately after status modifiers are removed, i.e. the pokemon's
        health should never exceed its max health.
        """
        result = []
        for modifier, rounds in self._stat_modifiers:
            if rounds > 1:
                result.append((modifier, rounds - 1))
        self._stat_modifiers = result
        self.modify_health(0)

    def rest(self) -> None:
        """Returns this pokemon to max health, removes any remaining status
        modifiers, and resets all move uses to their maximums."""
        self._health = self._stats.get_max_health()
        self._stat_modifiers = []

        # reset all move uses
        for move in self._moves:
            self._moves[move] = move.get_max_uses()

    def __str__(self) -> str:
        """Returns a simple representation of this pokemons name and level.
        
        Examples:
            >>> str(pokemon)
            'Pikachu (lv5)'
        """
        return f'{self._name} (lv{self._level})'

    def __repr__(self) -> str:
        """Returns a string representation of this pokemon"""
        return str(self)


class Trainer:
    """A class representing a pokemon trainer. A trainer can have 6 Pokemon
    at maximum.

    Notes:
        * The current pokemon should be kept track of with an instance variable
        representing the index of the currently selected Pokemon.
    
    Examples:
        >>> DEFAULT_STATS = (1, 100, 200, 200)
        >>> def create_pokemon(name):
        ...     return Pokemon(name, PokemonStats(DEFAULT_STATS), 'normal', moves=[])
        ...
        >>> ash = Trainer('Ash Ketchup')
        >>> ash.get_name()
        'Ash Ketchup'
        >>> ash.get_inventory()
        {}
        >>> ash.can_switch_pokemon(1)
        False
        >>> pikachu = create_pokemon("Pikachu")
        >>> ash.can_add_pokemon(pikachu)
        True
        >>> ash.get_all_pokemon()
        []
        >>> ash.add_pokemon(pikachu)
        >>> ash.get_all_pokemon()
        [Pikachu (lv1)]
        >>> ash.get_current_pokemon()
        Pikachu (lv1)
        >>> ash.can_add_pokemon(pikachu)
        False
        >>> for _ in range(5):
        ...     ash.add_pokemon(create_pokemon('jynx'))
        ...
        >>> ash.get_all_pokemon()
        [Pikachu (lv1), jynx (lv1), jynx (lv1), jynx (lv1), jynx (lv1), jynx (lv1)]
        >>> ash.get_current_pokemon()
        Pikachu (lv1)
        >>> ash.can_add_pokemon(create_pokemon('slugma'))
        False
        >>> ash
        Trainer('Ash Ketchup')
        >>> repr(ash)
        "Trainer('Ash Ketchup')"
        >>> brock = Trainer("Brock")
        >>> brock.get_current_pokemon()
        Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "a2.py", line X, in get_current_pokemon
            raise NoPokemonException()
        a2_support.NoPokemonException
    """

    def __init__(self, name: str) -> None:
        """Create an instance of the Trainer class.
        
        Parameters:
            * `name`: The name of the trainer.
        """
        self._name = name
        self._selected_pokemon = None
        self._pokemon = []
        self._inventory = {}  # <K,V> = <Items, uses>

    def get_name(self) -> str:
        """Return the trainer's name."""
        return self._name

    def get_inventory(self) -> Dict['Item', int]:
        """Returns the trainer's inventory as a dictionary mapping items to
        the count of that item remaining in the dictionary."""
        return self._inventory

    def get_current_pokemon(self) -> Pokemon:
        """Gets the current pokemon, or raises a NoPokemonException
        if the trainer doesn't have a single pokemon."""
        if self._selected_pokemon is None:
            raise NoPokemonException()
        return self._pokemon[self._selected_pokemon]

    def get_all_pokemon(self) -> List[Pokemon]:
        """Returns the trainer's pokemon.
        
        * The order of the pokemon in the list should be the order in which they
        were added to the roster.
        * Modifying the list returned by this method should not affect the state
        of this instance.
        """
        return self._pokemon[:]

    def rest_all_pokemon(self) -> None:
        """Rests all pokemon in the party"""
        for pokemon in self._pokemon:
            pokemon.rest()

    def all_pokemon_fainted(self) -> bool:
        """Return true iff all the trainer's pokemon have fainted."""
        for pokemon in self._pokemon:
            if not pokemon.has_fainted():
                return False
        return True

    def can_add_pokemon(self, pokemon: Pokemon) -> bool:
        """Returns true iff the supplied pokemon can be added to this trainer's
        roster.

        You shouldn't be able to add the same pokemon instance twice or more
        than the maximum amount of pokemon for a trainer.
        """
        if pokemon in self._pokemon:
            return False
        return len(self._pokemon) < MAXIMUM_POKEMON_ROSTER

    def add_pokemon(self, pokemon: Pokemon) -> None:
        """Adds a new pokemon into the roster, assuming that doing so
        would be valid. 
        
        If there were no Pokemon in the roster prior to calling this method,
        set the current pokemon to the one that was added.
        """
        self._pokemon.append(pokemon)

        # If this was our first pokemon, select it.
        if self._selected_pokemon is None:
            self._selected_pokemon = 0

    def can_switch_pokemon(self, index: int) -> bool:
        """Determines if the pokemon index would be valid to switch to,
        and returns true iff the switch would be valid.
        
        You cannot swap to a pokemon which is currently out on battle,
        or which has fainted.

        Parameters:
            * `index`: The index of the next pokemon in the roster.
        """
        # If index out of bounds
        if index < 0 or index >= len(self._pokemon):
            return False

        if index == self._selected_pokemon:
            return False

        return not self._pokemon[index].has_fainted()

    def switch_pokemon(self, index: int) -> None:
        """Switches pokemon to the one at the supplied index, assuming
        that the switch is valid.

        Parameters:
            * `index`: The index of the pokemon to switch to.
        """
        self._selected_pokemon = index

    def add_item(self, item: 'Item', uses: int) -> None:
        """Adds an item to the trainer's inventory and increments its uses by
        the supplied amount.

        Parameters:
            * `item`: The item to add.
            * `uses`: The quantity of the item to be added to the inventory.

        Examples:
            >>> food = Food("Burger King Foot Lettuce", 20)
            >>> ash.get_inventory()
            {}
            >>> ash.add_item(food, 1)
            >>> ash.get_inventory()
            {Food('Burger King Foot Lettuce'): 1}
            >>> ash.use_item(food)
            >>> ash.get_inventory()
            {}
            >>> ash.add_item(food, 3)
            >>> ash.add_item(food, 4)
            >>> ash.get_inventory()
            {Food('Burger King Foot Lettuce'): 7}
        """
        self._inventory[item] = self._inventory.get(item, 0) + uses

    def has_item(self, item: 'Item') -> bool:
        """Returns true if the item is in the trainer's inventory and has
        uses.
        """
        return item in self._inventory

    def use_item(self, item: 'Item') -> None:
        """If the item is present in the trainer's inventory, decrement its
        count. Removes the item from the inventory entirely if its count hits 0.
        """
        if not self.has_item(item):
            return

        self._inventory[item] -= 1
        if self._inventory[item] == 0:
            self._inventory.pop(item)

    def __str__(self) -> str:
        """Returns a string representation of a Trainer"""
        return f'Trainer({repr(self._name)})'

    def __repr__(self) -> str:
        """Returns a string representation of a Trainer"""
        return str(self)


class Battle:
    """A class which represents a pokemon battle. A battle can be between
    trainers or between a trainer and a wild pokemon. In this assignment,
    non-trainer battles are represented by a battle between 2 trainers, namely
    a regular trainer and  a 'dummy' trainer whose only pokemon is the wild
    pokemon.
    
    The main state-components of the battle are the action queue, and the turn:

    1. Pokemon battles aren't strictly turn-based, because the priority of each
    Action must be evaluated before they are performed. To make this happen,
    each round, each trainer adds their desired action to an `action queue`,
    and then the actions are performed in order of priority. In our 
    implementation, the trainers cannot add an action to the queue unless it is
    valid for them to do so, based on the `turn`, and if the action would be
    valid.
    2. The `turn` is the battle's way of determining who should be allowed
    to add actions to the action queue. Each round, the `turn` starts as None.
    The first time an action is performed by a trainer that round, the turn
    is set to the opposite trainer, becoming a boolean value which is True
    if the opposite trainer is the player, and False if they are the enemy.
    When the `turn` is a boolean, it means that only the trainer who it points
    to can add actions to the queue/enact them. When both trainers have enacted
    a valid action, the round is considered over, and the `turn` should be set
    to `None`.

    Examples:
        >>> DEFAULT_STATS = (1, 100, 200, 200)
        >>> def create_pokemon(name):
        ...      return Pokemon(name, PokemonStats(DEFAULT_STATS), 'normal', moves=[])
        ...
        >>> ash = Trainer("Ash")
        >>> brock = Trainer("Brock")
        >>> ash.add_pokemon(create_pokemon("pikachu"))
        >>> brock.add_pokemon(create_pokemon("geodude"))
        >>> battle = Battle(ash, brock, True)
        >>> print(battle.get_turn())
        None
        >>> battle.is_action_queue_empty()
        True
        >>> battle.is_over()
        False
        >>> battle.queue_action(Flee(), True)
        >>> battle.trainer_has_action_queued(True)
        True
        >>> battle.get_trainer(True)
        Trainer('Ash')
        >>> battle.get_trainer(False)
        Trainer('Brock')
        >>> battle.is_ready()
        False
        >>> battle.queue_action(Flee(), False)
        >>> battle.is_action_queue_full()
        True
        >>> battle.is_ready()
        True
        >>> summary = battle.enact_turn()
        >>> summary.get_messages()
        ['Unable to escape a trainer battle.']
        >>> battle.get_turn()
        False
        >>> battle.is_ready()
        True
        >>> battle.is_action_queue_full()
        False
        >>> other_summary = battle.enact_turn()
        >>> other_summary.get_messages()
        ['Unable to escape a trainer battle.']
        >>> print(battle.get_turn())
        None
    """

    def __init__(self, player: Trainer, enemy: Trainer,
                 is_trainer_battle: bool) -> None:
        """Creates an instance of a trainer battle.
        
        Parameters:
            * `player`: The trainer corresponding to the player character.
            * `enemy`: The enemy trainer.
            * `is_trainer_battle`: True iff the battle takes place between
                    trainers."""

        self._player = player
        self._enemy = enemy

        self._trainer_battle = is_trainer_battle
        self._finished_early = False

        self._turn = None
        self._action_queue = []

    def get_turn(self) -> Optional[bool]:
        """Get whose turn it currently is"""
        return self._turn

    def get_trainer(self, is_player: bool) -> Trainer:
        """Gets the trainer corresponding to the supplied parameter.
        
        Parameters:
            * `is_player`: True iff the trainer we want is the player.
        """
        return self._player if is_player else self._enemy

    def attempt_end_early(self) -> None:
        """Ends the battle early if it's not a trainer battle"""
        if not self._trainer_battle:
            self._finished_early = True

    def is_trainer_battle(self) -> bool:
        """Returns true iff the battle is between trainers"""
        return self._trainer_battle

    def is_action_queue_full(self) -> bool:
        """Returns true if both trainers have an action queued."""
        return len(self._action_queue) == 2

    def is_action_queue_empty(self) -> bool:
        """Returns true if neither trainer have an action queued."""
        return len(self._action_queue) == 0

    def trainer_has_action_queued(self, is_player: bool) -> bool:
        """Returns true iff the supplied trainer has an action queued

        Parameters:
            * `is_player`: True iff the trainer we want to check for is the
                    player.
        """
        for _, player in self._action_queue:
            if player == is_player:
                return True
        return False

    def is_ready(self) -> bool:
        """Returns true iff the next action is ready to be performed.
        
        The battle is deemed ready if neither trainer has performed an action
        this round and the action queue is full, or if one trainer has performed
        an action, and the other trainer is in the queue.
        """
        if self._turn is None:
            return self.is_action_queue_full()
        return self.trainer_has_action_queued(self._turn)

    def _update_turn(self, is_player) -> None:
        """Updates the turn state after the turn is over.
        """
        # If no players have made an action yet, set the turn to the opposite of
        # whoever just performed an action.
        if self._turn is None:
            self._turn = not is_player
        # Otherwise we reset the state for the next round.
        else:
            self._turn = None

    def queue_action(self, action: 'Action', is_player: bool) -> None:
        """Attempts to queue the supplied action if it's valid given the battle
        state, and came from the right trainer.

        An action is unable to be added to the queue if:
            The trainer is already in the queue;
            The queue is ready;
            The action is invalid given the game state;

        Parameters:
            * `action`: The action we are attempting to queue
            * `is_player`: True iff we're saying the action is going to be
                    performed by the player.
        """
        if (self.trainer_has_action_queued(is_player) or self.is_ready() or 
                not action.is_valid(self, is_player)):
            return

        self._action_queue.append((action, is_player))

    def _sort_actions(self) -> None:
        """Sorts the actions in the queue based on their priority."""
        if not self.is_action_queue_full():
            return

        self._action_queue.sort(key=lambda x: x[0].get_priority())

    def enact_turn(self) -> Optional['ActionSummary']:
        """Attempts to perform the next action in the queue,
        and returns a summary of its effects if it was valid.
        
        Notes:
            * If the next action in the queue is invalid, it should still
            be removed from the queue.
            * If this was the last turn to be performed that round,
            perform the post round actions.
        """
        if self.is_action_queue_empty():
            return

        self._sort_actions()

        # apply the next action, and update the battle state.
        next_action, is_player = self._action_queue.pop(0)
        if next_action.is_valid(self, is_player):
            result = next_action.apply(self, is_player)
            self._update_turn(is_player)
            # If it's a new round, update status effects.
            if self._turn is None:
                self._player.get_current_pokemon().post_round_actions()
                self._enemy.get_current_pokemon().post_round_actions()

            return result

    def is_over(self) -> bool:
        """Returns true iff the battle is over.
        
        A battle is over if all of the pokemon have
        fainted for either trainer, or if it ended early."""
        return (self._finished_early or self._player.all_pokemon_fainted()
                or self._enemy.all_pokemon_fainted())


class ActionSummary:
    """A class containing messages about actions and their effects.
    
    These messages are handled by the view to display information about the
    flow of the game.
    """

    def __init__(self, message: Optional[str] = None) -> None:
        """Constructs a new ActionSummary with an optional message.
        
        Parameters:
            * `message`: An optional message to be included.
        """
        self._messages = []
        if message is not None:
            self._messages.append(message)

    def get_messages(self) -> List[str]:
        """Returns a list of the messages contained within this summary.

        Examples:
            >>> msg = ActionSummary()
            >>> msg.get_messages()
            []
            >>> msg = ActionSummary("oh-wo")
            >>> msg.get_messages()
            ['oh-wo']
        """
        return self._messages

    def add_message(self, message: str) -> None:
        """Adds the supplied message to the ActionSummary instance.

        Parameters:
            * `message`: The message to add.
        
        Examples:
            >>> msg = ActionSummary()
            >>> msg.add_message("Action did a thing")
            >>> msg.get_messages()
            ['Action did a thing']
        """
        self._messages.append(message)

    def combine(self, summary: 'ActionSummary') -> None:
        """Combines two ActionSummaries. 
        
        The messages contained in the supplied summary should be added
        after those currently contained.

        Parameters:
            * `summary`: A summary containing the messages to add.
        
        Examples:
            >>> msg = ActionSummary('first')
            >>> msg2 = ActionSummary('second')
            >>> msg.combine(msg2)
            >>> msg.get_messages()
            ['first', 'second']
            >>> msg2.get_messages()
            [‘second’]
        """
        for message in summary.get_messages():
            self.add_message(message)


class Action:
    """An abstract class detailing anything which takes up a turn in battle.
    
    Applying an action can be thought of as moving the game from one state to
    the next.
    """

    def get_priority(self) -> int:
        """Returns the priority of this action, which is used to determine
        which action is performed first each round in the battle.
        
        Lower values of priority are 'quicker' than higher values,
        e.g. an Action with priority 0 happens before one with priority 1.

        You might want to take a look at the support code for a hint here."""
        return DEFAULT_ACTION_PRIORITY
    
    def is_valid(self, battle: 'Battle', is_player: bool) -> bool:
        """Determines if the action would be valid for the given trainer and
        battle state. Returns true iff it would be valid.
  
        By default, no action is valid if the game is over, or if it's not
        the trainer's turn.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this action.
        """
        if battle.is_over():
            return False

        return battle.get_turn() is None or battle.get_turn() == is_player

    def apply(self, battle: 'Battle', is_player: bool) -> ActionSummary:
        """Applies the action to the game state and returns a summary of
        the effects of doing so.
        
        On the base Action class, this method should raise a
        NotImplementedError.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this action.

        Examples:
            >>> action = Action()
            >>> action.apply(battle, True)
            Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
            File "a2.py", line X, in apply
                raise NotImplementedError()
            NotImplementedError
        """
        raise NotImplementedError()

    def _innards(self) -> str:
        """A helper method used in the string representation of this class
        to get what should appear inside the parentheses.
        """
        return ''

    def __str__(self) -> str:
        """Return a string representation of this class."""
        return f"{self.__class__.__name__}({self._innards()})"

    def __repr__(self) -> str:
        """Return a string representation of this class
        
        Examples:
            >>> action = Action()
            >>> str(action)
            'Action()'
            >>> repr(action)
            'Action()'
        """
        return str(self)


class Flee(Action):
    """An action where the trainer attempts to run away from the battle.
    
    Notes:
        * While it may still be valid, it has no effect in trainer battles.
        * If successful, this should end the battle early.

    Examples:
        >>> flee = Flee()
        >>> str(flee)
        'Flee()'
        >>> repr(flee)
        'Flee()'
    """

    def is_valid(self, battle: 'Battle', is_player: bool) -> bool:
        """Determines if an attempt to flee would be valid for a given
        battle state. Returns true iff it would be valid.

        Fleeing is considered a valid action if the base action validity checks
        pass, and the trainer's current pokemon has not fainted. This does not
        mean, however, that a trainer can flee trainer battles. In that case,
        fleeing is considered wasting a turn.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this item.
        """
        pokemon = battle.get_trainer(is_player).get_current_pokemon()
        return super().is_valid(battle, is_player) and not pokemon.has_fainted()

    def apply(self, battle: 'Battle', is_player: bool) -> ActionSummary:
        """The trainer attempts to flee the battle.
        
        The resulting message depends on whether or not the action was
        successful. See the support code for a hint.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this item.
        """
        battle.attempt_end_early()
        message = FLEE_INVALID if battle.is_trainer_battle() else FLEE_SUCCESS
        return ActionSummary(message=message)


class SwitchPokemon(Action):
    """An action representing the trainer's intention to switch pokemon.
    
    Examples:
        >>> switch = SwitchPokemon(2)
        >>> str(switch)
        'SwitchPokemon(2)'
        >>> repr(switch)
        'SwitchPokemon(2)'
    """

    def __init__(self, next_pokemon_index: int) -> None:
        """Creates an instance of the SwitchPokemon class.
        
        Parameters:
            * `next_pokemon_index`: The index of the pokemon the trainer wants
                    to switch to.
        """
        self._index = next_pokemon_index
        self._pokemon_name = None

    def is_valid(self, battle: 'Battle', is_player: bool) -> bool:
        """Determines if switching pokemon would be valid for a given
        trainer and battle state. Returns true iff it would be valid.

        After checking the validity requirements specified on the base Action
        class, switching delegates validity checking to the `Trainer` class.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this item.
        """
        if not super().is_valid(battle, is_player):
            return False

        trainer = battle.get_trainer(is_player)
        return trainer.can_switch_pokemon(self._index)

    def apply(self, battle: 'Battle', is_player: bool) -> ActionSummary:
        """The trainer switches pokemon, assuming that the switch would
        be valid.

        If the trainer using this action is the player, and their pokemon has
        not yet fainted, a message should be added to the action summary, in
        the form: `'{pokemon_name}, return!'`.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this action.
        """
        trainer = battle.get_trainer(is_player)
        pokemon = trainer.get_current_pokemon()
        next_pokemon = trainer.get_all_pokemon()[self._index]
        trainer.switch_pokemon(self._index)

        result = ActionSummary()
        if is_player and not pokemon.has_fainted():
            result.add_message(f"{pokemon.get_name()}, return!")
        result.add_message(
            f"{trainer.get_name()} switched to {next_pokemon.get_name()}.")
        return result

    def _innards(self) -> str:
        return repr(self._index)


class Item(Action):
    """An abstract class representing an Item, which a trainer may attempt
    to use to influence the battle.
    """

    def __init__(self, name: str) -> None:
        """Creates an Item.
        
        Parameters:
            * `name`: The name of this item
        """
        self._name = name

    def get_name(self) -> str:
        """Return the name of this item"""
        return self._name

    def is_valid(self, battle: 'Battle', is_player: bool) -> bool:
        """Determines if using the item would be a valid action for the given
        trainer and battle state. Returns true iff it would be valid.

        In addition to the validity requirements specified on the base Action
        class, `Item` and its subclasses are considered valid if:
            1. The trainer's current pokemon has not fainted.
            2. The item exists in the inventory of the trainer attempting to
            use it.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this item.
        """
        if not super().is_valid(battle, is_player):
            return False

        trainer = battle.get_trainer(is_player)
        pokemon = trainer.get_current_pokemon()

        # Make sure the player has that item in their inventory
        return not pokemon.has_fainted() and trainer.has_item(self)

    def decrement_item_count(self, trainer: 'Trainer') -> None:
        """Decrease the count of this item by one in the trainer's inventory
        
        Parameters:
            * `trainer`: The trainer attempting to use this item.
        """
        trainer.use_item(self)

    def _innards(self) -> str:
        return repr(self._name)


class Pokeball(Item):
    """An item which a trainer can use to attempt to catch wild pokemon.
    
    Examples:
        >>> pokeball = Pokeball("Master Ball", 1)
        >>> pokeball
        Pokeball('Master Ball')
        >>> str(pokeball)
        "Pokeball('Master Ball')"
        >>> repr(pokeball)
        "Pokeball('Master Ball')"
    """

    def __init__(self, name, catch_chance) -> None:
        """Creates a pokeball instance, used to catch pokemon in wild battles
        
        Parameters:
            * `name`: The name of this pokeball
            * `catch_chance`: The chance this pokeball has of catching a
                    pokemon.
        """
        super().__init__(name)
        self._catch_chance = catch_chance

    def apply(self, battle: 'Battle', is_player: bool) -> ActionSummary:
        """Attempt to catch the enemy pokemon and returns an ActionSummary
        containing information about the catch attempt.
        
        The returned summary will contain a
        different message based on the results of attempting to use the
        pokeball. See the support code for some hints as to what these messages
        might be.

        Notes:
            * No matter the result of the catch attempt, a pokeball will be
            used.
            * Catching pokemon is impossible in trainer battles.
            * The `did_succeed` method from the support code must be used to
            determine if a catch attempt was successful.
            * The wild pokemon will be added to the trainers roster if there is
            room
            * In a wild battle, catching the enemy pokemon will end the battle.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this item.
        """
        self.decrement_item_count(battle.get_trainer(is_player))
       
        if battle.is_trainer_battle():
            return ActionSummary(message=POKEBALL_INVALID_BATTLE_TYPE)

        enemy_pokemon = battle.get_trainer(not is_player).get_current_pokemon()
        name = enemy_pokemon.get_name()

        if not did_succeed(self._catch_chance):
            return ActionSummary(message=POKEBALL_UNSUCCESSFUL_CATCH.format(name))

        player = battle.get_trainer(is_player)
        if player.can_add_pokemon(enemy_pokemon):
            player.add_pokemon(enemy_pokemon)
            result = ActionSummary(message=POKEBALL_SUCCESSFUL_CATCH.format(name))
        else:
            result = ActionSummary(message=POKEBALL_FULL_TEAM.format(name))

        battle.attempt_end_early()
        return result


class Food(Item):
    """An Item which restores HP to the pokemon whose trainer uses it.
    
    Examples:
        >>> soup = Food("Good Soup", 69)
        >>> soup
        Food('Good Soup')
        >>> str(soup)
        "Food('Good Soup')"
        >>> repr(soup)
        "Food('Good Soup')"
    """

    def __init__(self, name: str, health_restored: int) -> None:
        """Create a Food instance.
        
        Parameters:
            * `name`: The name of this food.
            * `health_restored`: The number of health points restored when
                    a pokemon eats this piece of food.
        """
        super().__init__(name)
        self._health_restored = health_restored

    def apply(self, battle: 'Battle', is_player: bool) -> ActionSummary:
        """The trainer's current pokemon eats the food.

        Their current pokemon's health should consequently increase by the
        amount of health restored by this food.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this item.
        """
        pokemon = battle.get_trainer(is_player).get_current_pokemon()
        pokemon.modify_health(self._health_restored)
        self.decrement_item_count(battle.get_trainer(is_player))
        return ActionSummary(message=f'{pokemon.get_name()} ate {self._name}.')


class Move(Action):
    """An abstract class representing all learnable pokemon moves."""

    def __init__(self, name: str, element_type: str,
                 max_uses: int, speed: int) -> None:
        """Creates an instance of the Move class.

        Like pokemon, moves have a type which determines their effectiveness.
        They also have a speed which determines the move's priority.

        Parameters:
            * `name`: The name of this move
            * `element_type`: The name of the type of this move
            * `max_uses`: The number of time this move can be used before resting
            * `speed`: The speed of this move, with lower values corresponding
                    to faster moves priorities.
        """
        self._name = name
        self._element_type = element_type
        self._max_uses = max_uses
        self._speed = speed

    def get_name(self) -> str:
        """Return the name of this move"""
        return self._name

    def get_element_type(self) -> str:
        """Return the type of this move"""
        return self._element_type

    def get_max_uses(self) -> int:
        """Return the maximum times this move can be used"""
        return self._max_uses

    def get_priority(self) -> int:
        """Return the priority of this move.
        
        Moves have a speed-based priority. By default they are slower than other
        actions, with their total priority being calculated by adding the
        default speed-based action priority to the individual move's speed.
        """
        return SPEED_BASED_ACTION_PRIORITY + self._speed

    def is_valid(self, battle: 'Battle', is_player: bool) -> bool:
        """Determines if the move would be valid for the given trainer and
        battle state. Returns true iff it would be valid.

        In addition to the validity requirements specified on the base Action
        class, a `Move` is considered valid if:
            1. The trainer's current pokemon has not fainted.
            2. The trainer's current pokemon has learnt this move.
            3. The trainer's current pokemon has uses remaining for this move.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this action.
        """
        if not super().is_valid(battle, is_player):
            return False

        pokemon = battle.get_trainer(is_player).get_current_pokemon()
        if pokemon.has_fainted():
            return False

        # If the action is a move, make sure the player has that move and it has uses
        return pokemon.get_remaining_move_uses(self) != 0

    def apply(self, battle: 'Battle', is_player: bool) -> ActionSummary:
        """Applies the Move to the game state.

        Generally, the move should be performed and its effects should be
        applied to the player and/or the enemy if needed. In addition,
        the appropriate pokemon's remaining moves should be updated.

        Notes:
            * In the resulting ActionSummary, messages for ally effects should
            preceed enemy effects.

        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this action.
        """
        player = battle.get_trainer(is_player)
        enemy = battle.get_trainer(not is_player)

        pokemon = player.get_current_pokemon()
        result = ActionSummary(
            message=f'{pokemon.get_name()} used {self._name}.')

        # Order doesn't matter here.
        result.combine(self.apply_ally_effects(player))
        result.combine(self.apply_enemy_effects(player, enemy))

        player.get_current_pokemon().reduce_move_count(self)
        return result

    def apply_ally_effects(self, trainer: 'Trainer') -> ActionSummary:
        """Apply this move's effects to the ally trainer; if appropriate, and return
        the resulting ActionSummary.

        Parameters:
            * `trainer`: The trainer whose pokemon is using the move.
        """
        return ActionSummary()

    def apply_enemy_effects(self, trainer: 'Trainer',
                            enemy: 'Trainer') -> ActionSummary:
        """Apply this move's effects to the enemy; if appropriate, and return
        the resulting ActionSummary.

        Parameters:
            * `trainer`: The trainer whose pokemon is using the move.
            * `enemy`: The trainer whose pokemon is the target of the move.
        """
        return ActionSummary()
    
    def _innards(self) -> str:
        return f"{repr(self._name)}, {repr(self._element_type)}, {self._max_uses}"


class Attack(Move):
    """ A class representing damaging pokemon moves, that may be used against an 
    enemy pokemon. 
    
    Notes:
        * In addition to regular move requirements, attacking moves have a base
        damage and hit chance. 
        * Base damage is the damage this move would do
        before the pokemon's attack, defense or type effectiveness is accounted
        for. 
        * Hit chance is a measure of how likely the move is to hit an enemy
        pokemon, before the pokemon's hit chance stat is taken into account.
        * The `did_succeed` method from the support code must be used to
        determine if the attack hit.
        * If an attack 'misses' it does no damage to the enemy pokemon.

    Examples:
        >>> tackle = Attack('tackle', 'normal', 15, 100, 40, .95)
        >>> tackle.get_name()
        'tackle'
        >>> tackle.get_element_type()
        'normal'
        >>> tackle.get_max_uses()
        15
        >>> tackle.get_priority()
        101
        >>> str(tackle)
        "Attack('tackle', 'normal', 15)"
        >>> repr(tackle)
        "Attack('tackle', 'normal', 15)"
    """

    def __init__(self, name: str, element_type: str, max_uses: int, speed: int,
                 base_damage: int, hit_chance: float) -> None:
        """Creates an instance of an attacking move.
        
        Parameters:
            * `name`: The name of this move
            * `element_type`: The name of the type of this move
            * `max_uses`: The number of time this move can be used before resting
            * `speed`: The speed of this move, with lower values corresponding
                    to faster moves.
            * `base_damage`: The base damage of this move.
            * `hit_chance`: The base hit chance of this move.
        """
        super().__init__(name, element_type, max_uses, speed)
        self._base_damage = base_damage
        self._hit_chance = hit_chance

    def apply_enemy_effects(self, trainer: 'Trainer',
                            enemy: 'Trainer') -> ActionSummary:
        player_pokemon = trainer.get_current_pokemon()
        enemy_pokemon = enemy.get_current_pokemon()

        if not self.did_hit(player_pokemon):
            return ActionSummary(message=f"{player_pokemon.get_name()} missed!")

        result = ActionSummary()
        # Perform the damaging move
        damage = self.calculate_damage(player_pokemon, enemy_pokemon)
        enemy_pokemon.modify_health(-damage)

        if enemy_pokemon.has_fainted():
            exp = enemy_pokemon.experience_on_death()
            player_pokemon.gain_experience(exp)
            result.add_message(f"{enemy_pokemon.get_name()} has fainted.")
            # TODO Refactor so that exp gains only shown for the player.
            result.add_message(f"{player_pokemon.get_name()} gained {exp} exp.")

        return result

    def did_hit(self, pokemon: 'Pokemon') -> bool:
        """Determine if the move hit, based on the product of the pokemon's
        current hit chance, and the move's hit chance. Returns True iff it hits.

        Parameters:
            * `pokemon`: The attacking pokemon
        """
        pokemon_hit_chance = pokemon.get_stats().get_hit_chance()
        combined_hit_chance = pokemon_hit_chance * self._hit_chance
        return did_succeed(combined_hit_chance)

    def calculate_damage(self, pokemon: 'Pokemon',
                         enemy_pokemon: 'Pokemon') -> int:
        """Calculates what would be the total damage of using this move,
        assuming it hits, based on the stats of the attacking and defending
        pokemon.

        The damage formula is given by:
            `d * e * a / (D + 1)`, rounded down to the nearest integer,
            where:
            `d` is the move's base damage;
            `e` is the move's type effectiveness (see support code);
            `a` is the attacking pokemon's attack stat;
            `D` is the defending pokemon's defense stat.

        Parameters:
            * `pokemon`: The attacking trainer's pokemon
            * `enemy_pokemon`: The defending trainer's pokemon
        """
        effectiveness = ElementType.of(self._element_type).get_effectiveness(
                enemy_pokemon.get_element_type())
        pokemon_attack = pokemon.get_stats().get_attack()
        enemy_pokemon_defense = enemy_pokemon.get_stats().get_defense()

        return int(
            self._base_damage * effectiveness * pokemon_attack /
            (enemy_pokemon_defense + 1))


class StatusModifier(Move):
    """An abstract class to group commonalities between buffs and debuffs."""

    def __init__(self, name: str, element_type: str, max_uses: int, speed: int,
                 modification: Stats, rounds: int) -> None:
        """Creates an instance of this class
        
        Parameters:
            * `name`: The name of this move
            * `element_type`: The name of the type of this move
            * `max_uses`: The number of time this move can be used before resting
            * `speed`: The speed of this move, with lower values corresponding
                    to faster moves.
            * `modification`: A list of the same structure as
                    the `PokemonStats`, to be applied for the duration of the
                    supplied number of rounds.
            * `rounds`: The number of rounds for the modification
                    to be in effect.
        """
        super().__init__(name, element_type, max_uses, speed)
        self._modification = modification
        self._rounds = rounds


class Buff(StatusModifier):
    """Moves which buff the trainer's selected pokemon.
    
    A buff is a stat modifier that is applied to the pokemon using the move.

    Examples:
        >>> modifier = (0.2, 100, 100, 100)
        >>> meditate = Buff('meditate', 'psychic', 5, 80, modifier, 5)
        >>> meditate.get_name()
        'meditate'
        >>> meditate.get_element_type()
        'psychic'
        >>> meditate.get_max_uses()
        5
        >>> meditate.get_priority()
        81
        >>> str(meditate)
        "Buff('meditate', 'psychic', 5)"
        >>> repr(meditate)
        "Buff('meditate', 'psychic', 5)"
    """

    def apply_ally_effects(self, player: 'Trainer') -> ActionSummary:
        pokemon = player.get_current_pokemon()
        pokemon.add_stat_modifier(self._modification, self._rounds)
        return ActionSummary(
            message=f'{pokemon.get_name()} was buffed for {self._rounds} turns.')


class Debuff(StatusModifier):
    """Moves which debuff the enemy trainer's selected pokemon.
    
    A debuff is a stat modifier that is applied to the enemy pokemon which is
    the target of this move.

    Examples:
        >>> modifier = (0, -50, 0, -50)
        >>> toxic = Debuff('toxic', 'poison', 10, 70, modifier, 4)
        >>> toxic.get_name()
        'toxic'
        >>> toxic.get_element_type()
        'poison'
        >>> toxic.get_max_uses()
        10
        >>> toxic.get_priority()
        71
        >>> str(toxic)
        "Debuff('toxic', 'poison', 10)"
        >>> repr(toxic)
        "Debuff('toxic', 'poison', 10)"
    """

    def apply_enemy_effects(self, trainer: 'Trainer',
                            enemy: 'Trainer') -> ActionSummary:
        pokemon = enemy.get_current_pokemon()
        pokemon.add_stat_modifier(self._modification, self._rounds)
        return ActionSummary(
            message=f'{pokemon.get_name()} was debuffed for {self._rounds} turns.')


class Strategy:
    """An abstract class providing behaviour to determine a next action given a battle state."""

    def get_next_action(self, battle: Battle, is_player: bool) -> Action:
        """Determines and returns the next action for this strategy, given
        the battle state and trainer.

        This method should be overriden on subclasses.
        
        Parameters:
            * `battle`: The ongoing pokemon battle
            * `is_player`: True iff the player is using this action.
        """
        raise NotImplementedError()

    def _switch_to_next_pokemon(self, trainer: 'Trainer') -> Action:
        """
        Returns a new switch action based on the pokemon of a trainer

        Parameters:
            * `trainer`: Trainer whose pokemon is to be switched
        """
        for index, next_pokemon in enumerate(trainer.get_all_pokemon()):
            if not next_pokemon.has_fainted():
                return SwitchPokemon(index)


class ScaredyCat(Strategy):
    """(7030 Task) A strategy where the trainer always attempts to flee.
    
    Switches to the next available pokemon if the current one faints, and
    then keeps attempting to flee.
    """

    def get_next_action(self, battle: Battle, is_player: bool) -> Action:
        trainer = battle.get_trainer(is_player)
        if trainer.get_current_pokemon().has_fainted():
            return self._switch_to_next_pokemon(trainer)
        return Flee()


class TeamRocket(Strategy):
    """(7030 Task) A tough strategy used by Pokemon Trainers that are members
    of Team Rocket.
    
    Behaviour:
        1. Switch to the next available pokemon if the current one faints.
        2. Attempt to flee any wild battle.
        3. If the enemy trainer's current pokemon's name is 'pikachu', throw 
        pokeballs at it, if some exist in the inventory.
        4. Otherwise, use the first available move with an elemental type
        effectiveness greater than 1x against the defending pokemon's type.
        5. Otherwise, use the first available move with uses.
        6. Attempt to flee if the current pokemon has no moves with uses.
    """

    def get_next_action(self, battle: Battle, is_player: bool) -> Action:
        trainer = battle.get_trainer(is_player)
        pokemon = trainer.get_current_pokemon()
    
        if pokemon.has_fainted():
            return self._switch_to_next_pokemon(trainer)

        if not battle.is_trainer_battle():
            return Flee()

        # GET THE PIKACHU
        enemy_pokemon = battle.get_trainer(not is_player).get_current_pokemon()
        if enemy_pokemon.get_name().lower() == 'pikachu':
            for item in trainer.get_inventory():
                if issubclass(type(item), Pokeball):
                    return item

        # Check for super-effective moves
        for (move, uses) in pokemon.get_move_info():
            if uses == 0:
                continue
            element = ElementType.of(move.get_element_type())
            if element.get_effectiveness(enemy_pokemon.get_element_type()) > 1:
                return move

        # Check for regular moves
        for (move, uses) in pokemon.get_move_info():
            if uses != 0:
                return move

        return Flee()


def create_encounter(trainer: Trainer, wild_pokemon: Pokemon) -> Battle:
    """(7030 Task) Creates a Battle corresponding to an encounter with a wild
    pokemon.

    The enemy in this battle corresponds to a trainer with the empty string for
    a name, and whose only pokemon is the supplied wild pokemon. Masters students
    should leave this until they have completed all the non-masters classes.

    Parameters:
        * `trainer`: The adventuring trainer.
        * `wild_pokemon`: The pokemon that the player comes into contact with.
    """
    anonymous_trainer = Trainer("")
    anonymous_trainer.add_pokemon(wild_pokemon)
    return Battle(trainer, anonymous_trainer, False)

