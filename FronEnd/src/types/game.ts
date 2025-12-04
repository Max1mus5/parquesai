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
  winner_id: string | null;
}