import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import PokemonList from './components/DataPokemon'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
     <h1> Listado de Pokemon</h1> 

    <div><PokemonList /> </div>
     
    </>
  )
}

export default App
