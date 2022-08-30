-- @description Run detect pitch for open RS5K's 
-- @author Edgemeal
-- @noindex
-- Original script by Edgemeal, adjustments made by maxim.

function Main()-- RS5K button "Detect pitch" Command ID = 0x425
  local arr = reaper.new_array({}, 128)
  reaper.JS_Window_ArrayFind("Detect pitch", true, arr) 
  local adds = arr.table() 
  for i = 1, #adds do
    -- TODO: check if it is part of the currently selected track.
    reaper.JS_Window_OnCommand(reaper.JS_Window_GetParent(reaper.JS_Window_HandleFromAddress(adds[i])), 0x425)
  end 
end

if not reaper.APIExists('JS_Window_OnCommand') then
  reaper.MB('js_ReaScriptAPI extension is required for this script.', 'Missing API', 0) 
else


  Main()
end
reaper.defer(function () end)
