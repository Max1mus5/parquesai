export interface Game {
  id: string;
  name: string;
  status: string;
  max_players: number;
  current_players: number;
  is_private: boolean;
  created_by: string;
  created_at: string;
}

export interface GameCreateRequest {
  name: string;
  max_players: number;
  is_private: boolean;
  password?: string;
  creator_color: string;
}

export interface GameJoinRequest {
  color: string;
  password?: string;
}

export interface Player {
  id: string;
  name: string;
  color: string;
  score: number;
  pieces: Piece[];
  is_ai: boolean;
}

export interface Piece {
  id: string;
  position: number;
  status: string;
}

export interface GameState {
  id: string;
  status: string;
  players: Player[];
  current_player_id: string | null;
  board: { [key: number]: string[] };
  last_dice_value: number | null;
  last_dice1: number | null;
  last_dice2: number | null;
  is_pair: boolean;
  winner_id: string | null;
}

export interface DiceResult {
  dice1: number;
  dice2: number;
  total: number;
  is_pair: boolean;
  can_continue: boolean;
}