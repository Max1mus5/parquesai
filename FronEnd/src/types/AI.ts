export interface AddBotModalProps {
  gameId: string;
  isOpen: boolean;
  onClose: () => void;
  onBotAdded: () => void;
}
